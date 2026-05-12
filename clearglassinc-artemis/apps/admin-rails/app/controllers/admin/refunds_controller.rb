module Admin
  class RefundsController < ApplicationController
    before_action :require_mfa!
    before_action :require_admin!

    # POST /admin/refunds
    def create
      purchase = Purchase.find(params[:purchase_id])
      authorize_action!("billing.refund", purchase.policy_binding_id)

      RefundService.new(
        purchase: purchase,
        actor: current_user,
        reason: params.require(:reason)
      ).execute!

      render json: { ok: true }
    end

    private

    def require_mfa!
      head :forbidden unless current_user&.mfa_enabled?
    end

    def require_admin!
      head :forbidden unless current_user&.role == "admin"
    end
  end
end
