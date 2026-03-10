defmodule Stockpositive.Repo do
  use Ecto.Repo,
    otp_app: :stockpositive,
    adapter: Ecto.Adapters.Postgres
end
