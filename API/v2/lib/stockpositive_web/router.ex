defmodule StockpositiveWeb.Router do
  use StockpositiveWeb, :router

  pipeline :api do
    plug :accepts, ["json"]
  end

  pipeline :authenticated do
    plug StockpositiveWeb.Plugs.AuthenticateUser
  end

  scope "/users", StockpositiveWeb do
    pipe_through :api

    post "/register", UserController, :register
    post "/login", UserController, :login
  end

  scope "/users", StockpositiveWeb do
    pipe_through [:api, :authenticated]

    get "/me", UserController, :me
  end

  scope "/news", StockpositiveWeb do
    pipe_through [:api, :authenticated]

    get "/load-news", NewsController, :load_news
    get "/get-news", NewsController, :get_news
  end

  scope "/feeds", StockpositiveWeb do
    pipe_through [:api, :authenticated]

    post "/add_feed", FeedController, :add_feed
    delete "/delete_feed/:feed_id", FeedController, :delete_feed
    put "/edit_feed/:feed_id", FeedController, :edit_feed
    get "/get_feeds", FeedController, :get_feeds
    get "/get_all_feeds", FeedController, :get_all_feeds
  end
end
