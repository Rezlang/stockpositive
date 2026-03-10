import Config

if config_env() != :test do
  database_url =
    System.get_env("DATABASE_URL") ||
      raise "DATABASE_URL environment variable is not set"

  jwt_key =
    System.get_env("JWT_KEY") ||
      raise "JWT_KEY environment variable is not set"

  access_token_expire_minutes =
    System.get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "30") |> String.to_integer()

  config :stockpositive, Stockpositive.Repo,
    url: database_url,
    pool_size: String.to_integer(System.get_env("POOL_SIZE") || "10"),
    pool_pre_ping: true

  config :stockpositive, Stockpositive.Auth.Guardian,
    secret_key: jwt_key,
    token_ttl: %{"access" => {access_token_expire_minutes, :minutes}}
end

if config_env() == :test do
  test_database_url =
    System.get_env("TEST_DATABASE_URL") || System.get_env("DATABASE_URL")

  if test_database_url do
    config :stockpositive, Stockpositive.Repo,
      url: test_database_url
  end

  config :stockpositive, Stockpositive.Auth.Guardian,
    secret_key: System.get_env("JWT_KEY", "test_secret_key_for_testing_only"),
    token_ttl: %{"access" => {30, :minutes}}
end

if config_env() == :prod do
  config :stockpositive, StockpositiveWeb.Endpoint,
    http: [
      ip: {0, 0, 0, 0, 0, 0, 0, 0},
      port: String.to_integer(System.get_env("PORT") || "4000")
    ],
    secret_key_base:
      System.get_env("SECRET_KEY_BASE") ||
        raise("SECRET_KEY_BASE environment variable is not set")
end
