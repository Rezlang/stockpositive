defmodule Stockpositive.Schemas.UserGroup do
  use Ecto.Schema

  schema "usergroups" do
    field :name, :string
    field :description, :string

    has_many :permission_links, Stockpositive.Schemas.UserGroupPermission,
      foreign_key: :usergroup_id

    many_to_many :permissions, Stockpositive.Schemas.Permission,
      join_through: "usergroup_permissions"
  end
end
