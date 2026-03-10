defmodule StockpositiveWeb.Plugs.RequirePermissions do
  import Plug.Conn
  import Phoenix.Controller

  alias Stockpositive.Schemas.User

  def init(permissions), do: permissions

  def call(conn, required_permissions) do
    user = conn.assigns.current_user
    user_permissions = User.permissions(user)

    Enum.reduce_while(required_permissions, conn, fn perm, acc ->
      perm_value = Map.get(user_permissions, perm)
      has_perm = Map.has_key?(user_permissions, perm) and perm_value != 0

      if has_perm do
        {:cont, acc}
      else
        halted =
          conn
          |> put_status(403)
          |> json(%{detail: "Required permission missing or insufficient: #{perm}"})
          |> halt()

        {:halt, halted}
      end
    end)
  end
end
