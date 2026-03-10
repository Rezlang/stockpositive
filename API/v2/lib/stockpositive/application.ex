defmodule Stockpositive.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      Stockpositive.Repo,
      {Phoenix.PubSub, name: Stockpositive.PubSub},
      StockpositiveWeb.Endpoint
    ]

    opts = [strategy: :one_for_one, name: Stockpositive.Supervisor]
    Supervisor.start_link(children, opts)
  end

  @impl true
  def config_change(changed, _new, removed) do
    StockpositiveWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
