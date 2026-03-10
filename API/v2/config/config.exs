import Config

config :stockpositive, StockpositiveWeb.Endpoint,
  url: [host: "localhost"],
  adapter: Phoenix.Endpoint.Cowboy2Adapter,
  render_errors: [formats: [json: StockpositiveWeb.ErrorJSON], assigns: [format: "json"]],
  pubsub_server: Stockpositive.PubSub

config :stockpositive, Stockpositive.Repo,
  adapter: Ecto.Adapters.Postgres

config :stockpositive, Stockpositive.Auth.Guardian,
  issuer: "stockpositive"

config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

config :phoenix, :json_library, Jason

import_config "#{config_env()}.exs"
