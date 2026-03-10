defmodule Stockpositive.Accounts do
  import Ecto.Query

  alias Stockpositive.Repo
  alias Stockpositive.Auth
  alias Stockpositive.Schemas.{User, UserGroup}

  def get_user_by_email(email) do
    Repo.one(
      from u in User,
        where: u.email == ^email,
        preload: [usergroup: [permission_links: :permission], feeds: []]
    )
  end

  def get_user_by_username(username) do
    Repo.one(from u in User, where: u.username == ^username)
  end

  def get_user_by_phone(phone_number) do
    Repo.one(from u in User, where: u.phone_number == ^phone_number)
  end

  def get_user_by_identifier(identifier) do
    Repo.one(
      from u in User,
        where:
          u.email == ^identifier or u.username == ^identifier or
            u.phone_number == ^identifier,
        preload: [usergroup: [permission_links: :permission], feeds: []]
    )
  end

  def get_user_by_id(id) do
    User
    |> Repo.get(id)
    |> case do
      nil -> nil
      user -> Repo.preload(user, usergroup: [permission_links: :permission], feeds: [])
    end
  end

  def create_user(params) do
    with :ok <- ensure_email_available(params["email"]),
         :ok <- ensure_username_available(params["username"]),
         :ok <- ensure_phone_available(params["phone_number"]),
         {:ok, _} <- Auth.validate_password_strength(params["password"]) do
      default_group = get_or_create_default_group()
      hashed = Auth.hash_password(params["password"])

      %User{}
      |> User.changeset(%{
        username: params["username"],
        email: params["email"],
        phone_number: params["phone_number"],
        hashed_password: hashed,
        usergroup_id: default_group.id
      })
      |> Repo.insert()
      |> case do
        {:ok, user} -> {:ok, get_user_by_id(user.id)}
        {:error, changeset} -> {:error, changeset}
      end
    end
  end

  def update_user(user_id, params) do
    case get_user_by_id(user_id) do
      nil ->
        {:error, :not_found}

      user ->
        with :ok <- check_email_conflict(params["email"], user),
             :ok <- check_username_conflict(params["username"], user),
             :ok <- check_phone_conflict(params["phone_number"], user) do
          update_attrs = build_update_attrs(params, user)

          user
          |> User.changeset(update_attrs)
          |> Repo.update()
          |> case do
            {:ok, updated} -> {:ok, get_user_by_id(updated.id)}
            {:error, changeset} -> {:error, changeset}
          end
        end
    end
  end

  def delete_user(user_id) do
    case get_user_by_id(user_id) do
      nil ->
        {:error, :not_found}

      user ->
        Repo.delete(user)
        {:ok, true}
    end
  end

  def get_all_users(skip \\ 0, limit \\ 100) do
    Repo.all(from u in User, offset: ^skip, limit: ^limit)
  end

  defp ensure_email_available(nil), do: :ok

  defp ensure_email_available(email) do
    if Repo.one(from u in User, where: u.email == ^email, select: u.id),
      do: {:error, "Email already registered"},
      else: :ok
  end

  defp ensure_username_available(nil), do: :ok

  defp ensure_username_available(username) do
    if Repo.one(from u in User, where: u.username == ^username, select: u.id),
      do: {:error, "Username already taken"},
      else: :ok
  end

  defp ensure_phone_available(nil), do: :ok

  defp ensure_phone_available(phone) do
    if Repo.one(from u in User, where: u.phone_number == ^phone, select: u.id),
      do: {:error, "Phone number already registered"},
      else: :ok
  end

  defp check_email_conflict(nil, _user), do: :ok

  defp check_email_conflict(email, user) do
    if email != user.email do
      ensure_email_available(email)
    else
      :ok
    end
  end

  defp check_username_conflict(nil, _user), do: :ok

  defp check_username_conflict(username, user) do
    if username != user.username do
      ensure_username_available(username)
    else
      :ok
    end
  end

  defp check_phone_conflict(nil, _user), do: :ok

  defp check_phone_conflict(phone, user) do
    if phone != user.phone_number do
      ensure_phone_available(phone)
    else
      :ok
    end
  end

  defp build_update_attrs(params, user) do
    %{}
    |> put_if_present(:email, params["email"])
    |> put_if_present(:username, params["username"])
    |> put_if_present(:phone_number, params["phone_number"])
    |> then(fn attrs ->
      if params["password"] do
        Map.put(attrs, :hashed_password, Auth.hash_password(params["password"]))
      else
        attrs
      end
    end)
    |> Map.put_new(:email, user.email)
    |> Map.put_new(:username, user.username)
    |> Map.put_new(:hashed_password, user.hashed_password)
    |> Map.put_new(:usergroup_id, user.usergroup_id)
  end

  defp put_if_present(map, _key, nil), do: map
  defp put_if_present(map, key, value), do: Map.put(map, key, value)

  defp get_or_create_default_group do
    case Repo.get(UserGroup, 3) do
      nil ->
        {:ok, group} = Repo.insert(%UserGroup{name: "default_users"})
        group

      group ->
        group
    end
  end
end
