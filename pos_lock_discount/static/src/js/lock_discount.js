
odoo.define('pos_lock_mode.lock_mode', function (require) {
    "use strict";

	const NumpadWidget = require('point_of_sale.NumpadWidget');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
	var pos_model = require('point_of_sale.models');
	var SuperOrderline = pos_model.Orderline;
	var core = require('web.core');
	var _t = core._t;
	const { Gui } = require('point_of_sale.Gui');


    // Popup WebkulErrorPopup
    class WebkulErrorPopup extends AbstractAwaitablePopup {
		click_password_ok_button(event){
			this.cancel();
		}
    }
    WebkulErrorPopup.template = 'WebkulErrorPopup';
    WebkulErrorPopup.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(WebkulErrorPopup);

	// Inherit NumpadWidget----------------
    const PosResNumpadWidget = (NumpadWidget) =>
		class extends NumpadWidget {

        async wk_ask_password(password){
			var self = this;
			var ret = new $.Deferred();
			if (password) {
				const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
					isPassword: true,
					title: this.env._t('Password ?'),
					startingValue: null,
				});
				if (inputPin !== password) {
					Gui.showPopup('ErrorPopup',{
						'title':_t('Password Incorrect !!!'),
						'body':_('Entered Password Is Incorrect ')
					});
				} else {
					ret.resolve();
				}
			} else {
				ret.resolve();
			}
			return ret;
		}
			changeMode(mode) {
				var self = this;
				var order = this.env.pos.get_order();
			    var orderline_ids = order.get_orderlines();
                var employee = _.filter(self.env.pos.employees, function(employee){
				    return employee.id == self.env.pos.get_cashier().id;
			            });
				if(mode == 'discount' && orderline_ids){
					if(self.env.pos.config.discount_password && self.env.pos.config.lock_discount){
                         self.wk_ask_password(self.env.pos.config.discount_password).then(function(data){
                            console.log('success');
	                    for(var i=0; i< orderline_ids.length; i++){
					        	orderline_ids[i].set_discount(self.env.pos.config.admin_discount_rate);
				        	}
                         // super.changeMode(mode);
                           //return self.state.changeMode(mode);
                        });
					}
					else if(self.env.pos.config.lock_discount && self.env.pos.config.admin_discount_rate == 0 ){
						self.showPopup('ErrorPopup',{
							'title':self.env._t('No Discount Is Available'),
							'body':self.env._t('No discount is available for current POS. Please add discount from configuration')
						});
						//return;
						// super.changeMode(mode);
					}
					else  {
					super.changeMode(mode);
					}
				}
				else if(mode == 'discount'){
					self.showPopup('ErrorPopup',{
						'title':self.env._t('No Selected Orderline'),
						'body':self.env._t('No order line is Selected. Please add or select an Orderline')
					});
					//return;
				}
				else{
				super.changeMode(mode);
			//	return self.state.changeMode(mode);
				}
				//super.changeMode(mode);


			}


		};
    Registries.Component.extend(NumpadWidget, PosResNumpadWidget);

});
