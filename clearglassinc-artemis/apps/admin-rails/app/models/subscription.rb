class Subscription < ApplicationRecord
  enum status: {
    trialing: "trialing",
    active: "active",
    past_due: "past_due",
    canceled: "canceled"
  }

  validates :provider, inclusion: { in: %w[stripe gumroad] }
  validates :provider_customer_id, :plan_code, presence: true

  def cancel_with_audit!(actor_id:)
    transaction do
      update!(status: "canceled")
      AuditLog.create!(
        actor_id: actor_id,
        action: "subscription.canceled",
        target_type: "Subscription",
        target_id: id,
        metadata: { provider: provider }
      )
    end
  end
end
