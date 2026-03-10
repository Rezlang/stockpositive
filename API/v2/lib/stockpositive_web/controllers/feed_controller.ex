defmodule StockpositiveWeb.FeedController do
  use StockpositiveWeb, :controller

  alias Stockpositive.Feeds
  alias Stockpositive.Schemas.User

  plug StockpositiveWeb.Plugs.RequirePermissions, ["DELETE.FEED"] when action in [:delete_feed]
  plug StockpositiveWeb.Plugs.RequirePermissions, ["EDIT.FEED"] when action in [:edit_feed]
  plug StockpositiveWeb.Plugs.RequirePermissions, ["GET.FEEDS"] when action in [:get_feeds]
  plug StockpositiveWeb.Plugs.RequirePermissions, ["ADMIN.GET.FEEDS"] when action in [:get_all_feeds]

  def add_feed(conn, params) do
    user = conn.assigns.current_user
    permissions = User.permissions(user)

    case check_add_feed_permission(permissions, user) do
      :ok ->
        case Feeds.create_feed(params, user.id) do
          {:ok, feed} ->
            conn
            |> put_status(200)
            |> json(feed_response(feed))

          {:error, reason} ->
            {:error, reason}
        end

      {:error, message} ->
        conn
        |> put_status(403)
        |> json(%{detail: message})
    end
  end

  def delete_feed(conn, %{"feed_id" => feed_id}) do
    user = conn.assigns.current_user

    case Feeds.delete_feed(String.to_integer(feed_id), user.id) do
      {:ok, _} ->
        send_resp(conn, 204, "")

      {:error, :not_found, message} ->
        {:error, :not_found, message}

      {:error, :forbidden, message} ->
        {:error, :forbidden, message}
    end
  end

  def edit_feed(conn, %{"feed_id" => feed_id} = params) do
    user = conn.assigns.current_user
    update_attrs = build_update_attrs(params)

    case Feeds.update_feed(String.to_integer(feed_id), user.id, update_attrs) do
      {:ok, feed} ->
        json(conn, feed_response(feed))

      {:error, :not_found, message} ->
        {:error, :not_found, message}

      {:error, :forbidden, message} ->
        {:error, :forbidden, message}

      {:error, reason} ->
        {:error, reason}
    end
  end

  def get_feeds(conn, _params) do
    user = conn.assigns.current_user
    feeds = Feeds.get_user_feeds(user.id)
    json(conn, Enum.map(feeds, &feed_response/1))
  end

  def get_all_feeds(conn, _params) do
    feeds = Feeds.get_all_feeds()
    json(conn, Enum.map(feeds, &feed_response/1))
  end

  defp feed_response(feed) do
    %{
      id: feed.id,
      user_id: feed.user_id,
      feedname: feed.feedname,
      stocks: feed.stocks,
      sources: feed.sources,
      created_at: feed.created_at
    }
  end

  defp check_add_feed_permission(permissions, user) do
    perm_value = Map.get(permissions, "ADD.FEED")
    check_value = length(user.feeds) + 1

    cond do
      is_nil(perm_value) ->
        {:error, "Permission not found: ADD.FEED"}

      perm_value == -2 ->
        :ok

      perm_value < check_value ->
        {:error, "Permission ADD.FEED value insufficient (#{perm_value} < #{check_value})"}

      true ->
        :ok
    end
  end

  defp build_update_attrs(params) do
    %{}
    |> put_if_truthy("feedname", params["feedname"])
    |> put_if_truthy("stocks", params["stocks"])
    |> put_if_truthy("sources", params["sources"])
  end

  defp put_if_truthy(map, _key, nil), do: map
  defp put_if_truthy(map, _key, []), do: map
  defp put_if_truthy(map, _key, ""), do: map
  defp put_if_truthy(map, key, value), do: Map.put(map, key, value)
end
