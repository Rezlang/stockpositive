import Config

config :stockpositive, StockpositiveWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4002],
  secret_key_base: "test_secret_key_base_at_least_64_chars_long_for_testing_only_placeholder_xx"

config :stockpositive, Stockpositive.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "stockpositive_test",
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: 10

config :logger, level: :warning
