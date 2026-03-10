defmodule Stockpositive.Auth do
  alias Stockpositive.Auth.Guardian

  def verify_password(plain_password, hashed_password) do
    Bcrypt.verify_pass(plain_password, hashed_password)
  end

  def hash_password(password) do
    Bcrypt.hash_pwd_salt(password)
  end

  def create_access_token(user) do
    Guardian.encode_and_sign(user, %{}, token_type: "access")
  end

  def validate_password_strength(password) do
    cond do
      String.length(password) < 8 ->
        {:error, "password must be at least 8 characters long"}

      not Regex.match?(~r/\d/, password) ->
        {:error, "password must contain at least one digit"}

      not Regex.match?(~r/[A-Z]/, password) ->
        {:error, "password must contain at least one uppercase letter"}

      not Regex.match?(~r/[a-z]/, password) ->
        {:error, "password must contain at least one lowercase letter"}

      not Regex.match?(~r/[!@#$%^&*(),.?":{}|<>]/, password) ->
        {:error, "password must contain at least one special character"}

      true ->
        {:ok, password}
    end
  end
end
