defmodule Stockpositive.Feeds do
  import Ecto.Query

  alias Stockpositive.Repo
  alias Stockpositive.Schemas.UserFeed

  def get_owned_feed_or_error(id, user_id) do
    case Repo.get(UserFeed, id) do
      nil ->
        {:error, :not_found, "UserFeedORM not found"}

      feed ->
        if feed.user_id == user_id do
          {:ok, feed}
        else
          {:error, :forbidden, "Not authorized to access this UserFeedORM"}
        end
    end
  end

  def create_feed(attrs, user_id) do
    %UserFeed{}
    |> UserFeed.changeset(Map.put(attrs, "user_id", user_id))
    |> Repo.insert()
    |> case do
      {:ok, feed} -> {:ok, Repo.get!(UserFeed, feed.id)}
      {:error, changeset} -> {:error, changeset}
    end
  end

  def update_feed(id, user_id, attrs) do
    with {:ok, feed} <- get_owned_feed_or_error(id, user_id) do
      feed
      |> UserFeed.update_changeset(attrs)
      |> Repo.update()
      |> case do
        {:ok, updated} -> {:ok, Repo.get!(UserFeed, updated.id)}
        {:error, changeset} -> {:error, changeset}
      end
    end
  end

  def delete_feed(id, user_id) do
    with {:ok, feed} <- get_owned_feed_or_error(id, user_id) do
      Repo.delete(feed)
    end
  end

  def get_user_feeds(user_id) do
    Repo.all(from f in UserFeed, where: f.user_id == ^user_id)
  end

  def get_all_feeds do
    Repo.all(UserFeed)
  end
end
