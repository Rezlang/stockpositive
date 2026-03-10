defmodule StockpositiveWeb.NewsController do
  use StockpositiveWeb, :controller

  alias Stockpositive.News
  alias Stockpositive.Schemas.User

  plug StockpositiveWeb.Plugs.RequirePermissions, ["LOAD.NEWS"] when action in [:load_news]
  plug StockpositiveWeb.Plugs.RequirePermissions, ["GET.NEWS"] when action in [:get_news]

  def load_news(conn, params) do
    source = params["source"] || "market"
    symbols = parse_list_param(params["symbols"])

    case News.load_news(source, symbols) do
      {:ok, articles} ->
        json(conn, Enum.map(articles, &article_response/1))

      {:error, reason} ->
        conn
        |> put_status(502)
        |> json(%{detail: reason})
    end
  end

  def get_news(conn, params) do
    user = conn.assigns.current_user
    feed_id = String.to_integer(params["feedId"])
    before_date = parse_naive_datetime(params["beforeDate"])

    case News.get_news_for_feed(feed_id, user.id, before_date) do
      {:ok, result} ->
        json(conn, %{
          articles: Enum.map(result.articles, &article_response/1),
          next_cursor: result.next_cursor,
          has_more: result.has_more,
          total_returned: result.total_returned
        })

      {:error, :not_found, message} ->
        {:error, :not_found, message}

      {:error, :forbidden, message} ->
        {:error, :forbidden, message}
    end
  end

  defp article_response(nil), do: nil

  defp article_response(article) do
    %{
      id: article.id,
      title: article.title,
      description: article.description,
      content: article.content,
      link: article.link,
      imagelink: article.imagelink,
      keywords: article.keywords,
      creator: article.creator,
      symbols: article.symbols,
      pubdate: article.pubdate,
      sourcename: article.sourcename,
      sentiment: article.sentiment,
      aisummary: article.aisummary
    }
  end

  defp parse_list_param(nil), do: nil
  defp parse_list_param(value) when is_list(value), do: value
  defp parse_list_param(value) when is_binary(value), do: String.split(value, ",", trim: true)

  defp parse_naive_datetime(nil), do: nil

  defp parse_naive_datetime(str) when is_binary(str) do
    cleaned = String.replace(str, "Z", "")

    case NaiveDateTime.from_iso8601(cleaned) do
      {:ok, dt} -> dt
      _ -> nil
    end
  end
end
