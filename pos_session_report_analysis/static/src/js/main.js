/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_session_report_analysis.env.pos_session_report_analysis',function(require){
    "use strict"
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useListener } = require('web.custom_hooks');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    var _t = core._t;




    class SessionReportButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        get currentOrder(){
            return this.env.pos.get_order();
        }
        async onClick() {
            var session_id = this.env.pos.pos_session.id;
            if(session_id){
                var  self = this;
                if(self.env.pos.config.iface_print_via_prroxy){
                    rpc.query({
                        model:'pos.session',
                        method:'get_session_report_data',
                        args: [{ 'session_id': session_id }]
                    })
                    .then(function(result){
                       if(result){
                            var company = {
                                email: self.env.pos.company.email,
                                website: self.env.pos.company.website,
                                company_registry: self.env.pos.company.company_registry,
                                contact_address: self.env.pos.company.partner_id[1],
                                vat: self.env.pos.company.vat,
                                phone: self.env.pos.company.phone,
                                name: self.env.pos.company.name,
                                logo:  self.env.pos.company_logo_base64,
                            }
                            result['company'] = company;
                            result['widget'] = self;
                            var receipt = QWeb.render('SessionXmlReceipt', result);
                            console.log("receipt",receipt)
                            console.log('receipt',receipt)
                            self.env.pos.proxy.print_receipt(receipt);
                       }
                        
                    });
                }
                else{
                    setTimeout(function(){
                        self.env.pos.do_action('pos_session_report_analysis.action_wk_report_pos_session_summary',{additional_context:{ 
                            active_ids:[session_id],
                        }})    
                        .catch(function(err){
                            console.log("error",err)
                            self.showPopup('ErrorPopup', {
                                'title': _t('The report could not be printed'),
                                'body': _t('Check your internet connection and try again.'),
                            });
                        });
                    },500)
                }

            }
           
        }
        generate_wrapped_product_name(data) {
			var MAX_LENGTH =24;
			var wrapped = [];
			var name = data;
			var current_line = "";
	
			while (name.length > 0) {
				var space_index = name.indexOf(" ");
	
				if (space_index === -1) {
					space_index = name.length;
				}
	
				if (current_line.length + space_index > MAX_LENGTH) {
					if (current_line.length) {
						wrapped.push(current_line);
					}
					current_line = "";
				}
	
				current_line += name.slice(0, space_index + 1);
				name = name.slice(space_index + 1);
			}
	
			if (current_line.length) {
				wrapped.push(current_line);
			}
	
			return wrapped;
		}

    }
    SessionReportButton.template = 'SessionReportButton';

    ProductScreen.addControlButton({
        component: SessionReportButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(SessionReportButton);

    return SessionReportButton;

});