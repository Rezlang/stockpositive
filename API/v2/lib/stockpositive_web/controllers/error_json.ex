defmodule StockpositiveWeb.ErrorJSON do
  def render("404.json", _assigns), do: %{detail: "Not Found"}
  def render("500.json", _assigns), do: %{detail: "Internal Server Error"}
  def render(template, _assigns), do: %{detail: Phoenix.Controller.status_message_from_template(template)}
end
