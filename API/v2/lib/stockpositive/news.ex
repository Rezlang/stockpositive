defmodule Stockpositive.News do
  import Ecto.Query
  require Logger

  alias Stockpositive.Repo
  alias Stockpositive.Feeds
  alias Stockpositive.News.DataClient
  alias Stockpositive.Schemas.NewsArticle

  @page_size 10
  @max_symbols_per_api_call 5
  @max_sources_per_api_call 5
  @max_api_batches 2

  @domain_to_source_name %{
    "finance.yahoo.com" => "YAHOOFINANCE",
    "bloomberg.com" => "BLOOMBERG",
    "reuters.com" => "REUTERS",
    "cnbc.com" => "CNBC",
    "fool.com" => "FOOLCOM",
    "coinmarketcap.com" => "COINMARKETCAP",
    "binance.com" => "BINANCE",
    "investing.com" => "INVESTINGCOM"
  }

  def load_news(source, symbols) do
    case DataClient.retrieve_news(source, symbols) do
      {:ok, articles} ->
        stored = Enum.map(articles, &create_article/1)
        {:ok, stored}

      {:error, reason} ->
        {:error, reason}
    end
  end

  def get_news_for_feed(feed_id, current_user_id, before_date) do
    Logger.info("Fetching news for feedId=#{feed_id}, userId=#{current_user_id}")

    with {:ok, feed} <- Feeds.get_owned_feed_or_error(feed_id, current_user_id) do
      symbols = feed.stocks || []
      sources = feed.sources || []

      Logger.info("Feed symbols: #{inspect(symbols)}, sources: #{inspect(sources)}")

      articles = query_articles(symbols, sources, before_date, 2 * @page_size)
      deduplicated = deduplicate_by_id(articles)

      deduplicated =
        if length(deduplicated) < @page_size do
          IO.puts("Only #{length(deduplicated)} articles found, fetching more from API...")
          stored = fetch_and_store_articles(symbols, sources)
          IO.puts("Stored #{stored} new articles from API")

          symbols
          |> query_articles(sources, before_date, 2 * @page_size)
          |> deduplicate_by_id()
        else
          deduplicated
        end

      response_articles = Enum.take(deduplicated, @page_size)
      remaining = Enum.drop(deduplicated, @page_size)

      has_more = length(remaining) > 0

      next_cursor =
        if response_articles != [] and has_more do
          List.last(response_articles).pubdate
        else
          nil
        end

      if length(remaining) < @page_size and length(response_articles) == @page_size do
        Logger.info("Only #{length(remaining)} articles remaining, fetching more for next request...")
        fetch_and_store_articles(symbols, sources)
      end

      Logger.info("Returning #{length(response_articles)} articles, hasMore=#{has_more}")

      {:ok,
       %{
         articles: response_articles,
         next_cursor: next_cursor,
         has_more: has_more,
         total_returned: length(response_articles)
       }}
    end
  end

  def create_article(attrs) do
    %NewsArticle{}
    |> NewsArticle.changeset(attrs)
    |> Repo.insert()
    |> case do
      {:ok, article} -> article
      {:error, _} -> nil
    end
  end

  defp query_articles(symbols, sources, before_date, limit) do
    query =
      from a in NewsArticle,
        order_by: [desc: a.pubdate, desc: a.id],
        limit: ^limit

    query =
      if symbols != [] do
        where(query, [a], fragment("? && ?", a.symbols, ^symbols))
      else
        query
      end

    query =
      if sources != [] do
        db_sources =
          Enum.map(sources, fn s ->
            Map.get(@domain_to_source_name, String.downcase(s), DataClient.normalize_source_name(s))
          end)

        where(query, [a], a.sourcename in ^db_sources)
      else
        query
      end

    query =
      if before_date do
        where(query, [a], a.pubdate < ^before_date)
      else
        query
      end

    Repo.all(query)
  end

  defp create_random_batches(symbols, sources) do
    if symbols == [] and sources == [] do
      []
    else
      shuffled_symbols = Enum.shuffle(symbols)
      shuffled_sources = Enum.shuffle(sources)

      fits_in_one =
        length(shuffled_symbols) <= @max_symbols_per_api_call and
          length(shuffled_sources) <= @max_sources_per_api_call

      if fits_in_one do
        [{shuffled_symbols, shuffled_sources}]
      else
        for i <- 0..(@max_api_batches - 1) do
          sym_start = i * @max_symbols_per_api_call
          src_start = i * @max_sources_per_api_call

          batch_symbols = Enum.slice(shuffled_symbols, sym_start, @max_symbols_per_api_call)
          batch_sources = Enum.slice(shuffled_sources, src_start, @max_sources_per_api_call)

          {batch_symbols, batch_sources}
        end
        |> Enum.filter(fn {syms, srcs} -> syms != [] or srcs != [] end)
      end
    end
  end

  defp fetch_and_store_articles(symbols, sources) do
    batches =
      if symbols == [] do
        [{[], sources}]
      else
        create_random_batches(symbols, sources)
      end

    Enum.reduce(batches, 0, fn {batch_symbols, _batch_sources}, total_stored ->
      IO.puts("Fetching news for symbols=#{inspect(batch_symbols)}, sources=#{inspect(_batch_sources)}")

      case DataClient.retrieve_news("market", if(batch_symbols != [], do: batch_symbols, else: nil), nil) do
        {:ok, articles} ->
          IO.puts("API returned #{length(articles)} articles")

          new_count =
            Enum.reduce(articles, 0, fn article_attrs, count ->
              existing =
                Repo.one(
                  from a in NewsArticle,
                    where: a.link == ^article_attrs.link,
                    select: a.id
                )

              if is_nil(existing) do
                create_article(article_attrs)
                count + 1
              else
                count
              end
            end)

          IO.puts("Stored #{total_stored + new_count} new articles from batch")
          total_stored + new_count

        {:error, reason} ->
          IO.puts("Failed to fetch news for batch symbols=#{inspect(batch_symbols)}: #{reason}")
          total_stored
      end
    end)
  end

  defp deduplicate_by_id(articles) do
    {deduped, _} =
      Enum.reduce(articles, {[], MapSet.new()}, fn article, {acc, seen} ->
        if MapSet.member?(seen, article.id) do
          {acc, seen}
        else
          {acc ++ [article], MapSet.put(seen, article.id)}
        end
      end)

    deduped
  end
end
