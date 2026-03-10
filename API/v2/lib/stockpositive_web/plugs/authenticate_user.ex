defmodule StockpositiveWeb.Plugs.AuthenticateUser do
  import Plug.Conn
  import Phoenix.Controller

  alias Stockpositive.Auth.Guardian

  def init(opts), do: opts

  def call(conn, _opts) do
    with ["Bearer " <> token] <- get_req_header(conn, "authorization"),
         {:ok, claims} <- Guardian.decode_and_verify(token),
         {:ok, user} <- Guardian.resource_from_claims(claims) do
      if user.is_active do
        IO.puts("Permissions: #{inspect(Stockpositive.Schemas.User.permissions(user))}")
        assign(conn, :current_user, user)
      else
        conn
        |> put_status(400)
        |> json(%{detail: "Inactive user"})
        |> halt()
      end
    else
      _ ->
        conn
        |> put_status(401)
        |> json(%{detail: "Could not validate credentials"})
        |> put_resp_header("www-authenticate", "Bearer")
        |> halt()
    end
  end
end
