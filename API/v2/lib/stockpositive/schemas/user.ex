defmodule Stockpositive.Schemas.User do
  use Ecto.Schema
  import Ecto.Changeset

  schema "users" do
    field :username, :string
    field :email, :string
    field :phone_number, :string
    field :hashed_password, :string
    field :is_active, :boolean, default: true
    field :created_at, :utc_datetime

    belongs_to :usergroup, Stockpositive.Schemas.UserGroup
    has_many :feeds, Stockpositive.Schemas.UserFeed
  end

  def changeset(user, attrs) do
    user
    |> cast(attrs, [:username, :email, :phone_number, :hashed_password, :is_active, :usergroup_id])
    |> validate_required([:username, :email, :hashed_password, :usergroup_id])
    |> validate_format(:email, ~r/@/)
    |> unique_constraint(:email)
    |> unique_constraint(:username)
    |> unique_constraint(:phone_number)
  end

  def permissions(%__MODULE__{usergroup: %{permission_links: links}}) when is_list(links) do
    Map.new(links, fn link -> {link.permission.name, link.permission_value} end)
  end

  def permissions(_), do: %{}
end
