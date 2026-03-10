defmodule Stockpositive.Schemas.NewsArticle do
  use Ecto.Schema
  import Ecto.Changeset

  schema "news" do
    field :title, :string
    field :description, :string
    field :content, :string
    field :link, :string
    field :imagelink, :string
    field :keywords, {:array, :string}
    field :creator, {:array, :string}
    field :symbols, {:array, :string}
    field :pubdate, :naive_datetime
    field :sourcename, :string
    field :sentiment, :string
    field :aisummary, :string
  end

  def changeset(article, attrs) do
    article
    |> cast(attrs, [
      :title,
      :description,
      :content,
      :link,
      :imagelink,
      :keywords,
      :creator,
      :symbols,
      :pubdate,
      :sourcename,
      :sentiment,
      :aisummary
    ])
  end
end
