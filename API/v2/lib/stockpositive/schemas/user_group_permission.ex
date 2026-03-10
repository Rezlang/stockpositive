defmodule Stockpositive.Schemas.UserGroupPermission do
  use Ecto.Schema

  @primary_key false
  schema "usergroup_permissions" do
    field :permission_value, :integer

    belongs_to :usergroup, Stockpositive.Schemas.UserGroup
    belongs_to :permission, Stockpositive.Schemas.Permission
  end
end
