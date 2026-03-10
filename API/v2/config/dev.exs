import Config

config :stockpositive, StockpositiveWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4000],
  check_origin: false,
  debug_errors: true,
  secret_key_base: "dev_secret_key_base_at_least_64_chars_long_for_development_only_placeholder"

config :stockpositive, Stockpositive.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "stockpositive_dev",
  show_sensitive_data_on_connection_error: true,
  pool_size: 10

config :logger, level: :debug
