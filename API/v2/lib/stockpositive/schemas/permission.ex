defmodule Stockpositive.Schemas.Permission do
  use Ecto.Schema

  schema "permissions" do
    field :name, :string
    field :description, :string

    has_many :usergroup_links, Stockpositive.Schemas.UserGroupPermission,
      foreign_key: :permission_id
  end
end
