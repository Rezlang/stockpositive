defmodule Stockpositive.Auth.Guardian do
  use Guardian, otp_app: :stockpositive

  def subject_for_token(user, _claims), do: {:ok, user.email}

  def resource_from_claims(%{"sub" => email}) do
    case Stockpositive.Accounts.get_user_by_email(email) do
      nil -> {:error, :resource_not_found}
      user -> {:ok, user}
    end
  end
end
