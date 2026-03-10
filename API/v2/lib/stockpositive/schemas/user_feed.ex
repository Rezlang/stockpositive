defmodule Stockpositive.Schemas.UserFeed do
  use Ecto.Schema
  import Ecto.Changeset

  schema "userfeeds" do
    field :feedname, :string
    field :stocks, {:array, :string}
    field :sources, {:array, :string}
    field :created_at, :utc_datetime

    belongs_to :user, Stockpositive.Schemas.User
  end

  def changeset(feed, attrs) do
    feed
    |> cast(attrs, [:feedname, :stocks, :sources, :user_id])
    |> validate_required([:feedname, :stocks, :sources, :user_id])
    |> validate_length(:feedname, min: 1)
  end

  def update_changeset(feed, attrs) do
    feed
    |> cast(attrs, [:feedname, :stocks, :sources])
  end
end
