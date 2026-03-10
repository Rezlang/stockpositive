defmodule StockpositiveWeb.UserController do
  use StockpositiveWeb, :controller

  alias Stockpositive.Accounts
  alias Stockpositive.Auth
  alias Stockpositive.Schemas.User

  def register(conn, params) do
    case Accounts.create_user(params) do
      {:ok, user} ->
        conn
        |> put_status(201)
        |> json(user_response(user))

      {:error, reason} ->
        {:error, reason}
    end
  end

  def login(conn, %{"username" => email, "password" => password}) do
    user = Accounts.get_user_by_email(email)

    if user && Auth.verify_password(password, user.hashed_password) do
      case Auth.create_access_token(user) do
        {:ok, token, _claims} ->
          json(conn, %{access_token: token, token_type: "bearer"})

        {:error, _reason} ->
          conn
          |> put_status(401)
          |> json(%{detail: "Incorrect email or password"})
          |> put_resp_header("www-authenticate", "Bearer")
      end
    else
      conn
      |> put_status(401)
      |> json(%{detail: "Incorrect email or password"})
      |> put_resp_header("www-authenticate", "Bearer")
    end
  end

  def me(conn, _params) do
    json(conn, user_response(conn.assigns.current_user))
  end

  defp user_response(user) do
    %{
      id: user.id,
      username: user.username,
      email: user.email,
      phone_number: user.phone_number,
      usergroup_id: user.usergroup_id,
      is_active: user.is_active,
      created_at: user.created_at,
      permissions: User.permissions(user)
    }
  end
end
