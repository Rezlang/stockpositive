defmodule Stockpositive.News.DataClient do
  @news_api_url "https://newsdata.io/api/1/market"

  def normalize_source_name(nil), do: nil

  def normalize_source_name(name) do
    name
    |> String.upcase()
    |> String.trim()
    |> String.replace(~r/[^A-Z0-9]/, "")
  end

  def retrieve_news(source \\ "market", symbols \\ nil, domainurls \\ nil) do
    api_key = Application.get_env(:stockpositive, :newsdata_api_key)

    params =
      %{
        apikey: api_key,
        q: source,
        language: "en",
        sort: "pubdateasc",
        removeduplicate: 1
      }
      |> put_if_present(:symbol, symbols && Enum.join(symbols, ","))
      |> put_if_present(:domainurl, domainurls && Enum.join(domainurls, ","))

    case Req.get(@news_api_url, params: params, receive_timeout: 10_000) do
      {:ok, %{status: status, body: body}} when status in 200..299 ->
        articles = body |> Map.get("results", []) |> Enum.map(&parse_article/1)
        {:ok, articles}

      {:ok, %{status: status}} ->
        {:error, "NewsData API returned status #{status}"}

      {:error, reason} ->
        {:error, inspect(reason)}
    end
  end

  defp parse_article(item) do
    pubdate =
      case item["pubDate"] do
        nil ->
          nil

        str when is_binary(str) ->
          case NaiveDateTime.from_iso8601(String.replace(str, "Z", "")) do
            {:ok, dt} -> dt
            _ -> nil
          end
      end

    %{
      title: item["title"],
      description: item["description"],
      content: item["content"],
      link: item["link"],
      imagelink: item["image_url"],
      keywords: normalize_string_or_list(item["keywords"]),
      creator: normalize_string_or_list(item["creator"]),
      symbols: normalize_string_or_list(item["symbol"]),
      pubdate: pubdate,
      sourcename: normalize_source_name(item["source_name"]),
      sentiment: item["sentiment"],
      aisummary: item["ai_summary"]
    }
  end

  defp normalize_string_or_list(nil), do: nil

  defp normalize_string_or_list(value) when is_binary(value) do
    [String.upcase(value)]
  end

  defp normalize_string_or_list(values) when is_list(values) do
    Enum.map(values, fn
      v when is_binary(v) -> String.upcase(v)
      v -> v
    end)
  end

  defp put_if_present(map, _key, nil), do: map
  defp put_if_present(map, key, value), do: Map.put(map, key, value)
end
