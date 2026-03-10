defmodule StockpositiveWeb.FallbackController do
  use Phoenix.Controller

  def call(conn, {:error, :not_found}) do
    conn
    |> put_status(404)
    |> json(%{detail: "Not found"})
  end

  def call(conn, {:error, :not_found, message}) do
    conn
    |> put_status(404)
    |> json(%{detail: message})
  end

  def call(conn, {:error, :forbidden, message}) do
    conn
    |> put_status(403)
    |> json(%{detail: message})
  end

  def call(conn, {:error, message}) when is_binary(message) do
    conn
    |> put_status(400)
    |> json(%{detail: message})
  end

  def call(conn, {:error, %Ecto.Changeset{} = changeset}) do
    errors =
      Ecto.Changeset.traverse_errors(changeset, fn {msg, opts} ->
        Enum.reduce(opts, msg, fn {key, value}, acc ->
          String.replace(acc, "%{#{key}}", to_string(value))
        end)
      end)

    conn
    |> put_status(422)
    |> json(%{detail: "Validation failed", errors: errors})
  end
end
