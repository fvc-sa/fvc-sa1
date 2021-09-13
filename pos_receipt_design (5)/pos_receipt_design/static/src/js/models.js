

odoo.define('wk_pos_invoice_offline.models', function (require) {
    "use strict"
    var models = require('point_of_sale.models');
    var PosDB = require("point_of_sale.DB");
    const Registries = require('point_of_sale.Registries');
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const { nextFrame } = require('point_of_sale.utils');
    var rpc = require('web.rpc')

    models.load_models([{
        model: 'receipt.design',
        loaded: function(self, designs) {
            self.db.all_designs = designs;
            self.db.receipt_by_id = {};
            designs.forEach(function(design){
                self.db.receipt_by_id[design.id] = design;
            });
        },
    }])

    PosDB.include({
        init: function(options){
            var self = this;
            this._super(options);
            this.receipt_design = null;
        },
    })

    // Inherit AbstractReceiptScreen
    const PosResAbstractReceiptScreen = (AbstractReceiptScreen) =>
        class extends AbstractReceiptScreen{


         async  doTask(imgUrl){
                        var fullurl='/report/ajaxqr/?value='+ imgUrl;
                        var result='';
                          await $.ajax({
                                type: "GET",
                                url: fullurl,
                                success: function(response){
                                    result= response;
                                }
                        });
                        return result;
                    }
            async _printReceipt() {
                var self = this;
                if(!self.env.pos.config.use_custom_receipt){
                    var data = super._printReceipt();
                    return data
                }
                else {
                    //if (self.env.pos.proxy.printer) {
                        var receipt_design_id = self.env.pos.config.receipt_design_id[0];
                        var receipt_design = self.env.pos.db.receipt_by_id[receipt_design_id].receipt_design;
                        var order = self.env.pos.get_order();
                        var companyname =order.export_for_printing().company.name;
                        var companyvat =order.export_for_printing().company.vat;
                        var orderdate=order.export_for_printing().date.localestring;
                        var ordertotalincl=order.export_for_printing().total_with_tax;
                        var ordertax=order.export_for_printing().total_tax;
                        var qrcodedata=companyname +' '+ companyvat +' '+ orderdate +' '+ ordertotalincl.toFixed(2) +' '+ ordertax.toFixed(2) ;


                        var  qrcodeimg = await this.doTask(qrcodedata);
                        if(!qrcodeimg){

                            console.log('not qrcodeimg');

                        }
                        else{
                            qrcodeimg ='data:image/png;base64,' + qrcodeimg ;

                        }
                        var data = { widget: self.env,
                            pos: order.pos,
                            order: order,
                            receipt: order.export_for_printing(),
                            orderlines: order.get_orderlines(),
                            qrcode :qrcodedata,
                            qrcodeimg:qrcodeimg,
                            paymentlines: order.get_paymentlines(), };

                        var parser = new DOMParser();
                        var xmlDoc = parser.parseFromString(receipt_design,"text/xml");

                        var s = new XMLSerializer();
                        var newXmlStr = s.serializeToString(xmlDoc);

                        //Works using the DOMParser
                        var qweb = new QWeb2.Engine();
                        qweb.add_template('<templates><t t-name="receipt_design">'+newXmlStr+'</t></templates>');

                        var receipt = qweb.render('receipt_design',data);
                         setTimeout(function(){

                           },1000);

                        console.log(receipt);

                       if (self.env.pos.proxy.printer){

                        const printResult =  await self.env.pos.proxy.printer.print_receipt(receipt);
                        if (printResult !='undefined' && printResult.successful) {

                            return true;
                        }
                        }

                     else {
                            const { confirmed } = await self.showPopup('ConfirmPopup', {
                                title: 'طباعة الفاتورة',
                                body: 'Do you want to print using the web printer?',
                            });
                            if (confirmed) {
                                // We want to call the _printWeb when the popup is fully gone
                                // from the screen which happens after the next animation frame.
                                await nextFrame();
                                return await self._printWeb();
                            }
                            return false;
                        }

                   // } else {
                     //   return await self._printWeb();
                    //}
                }
            }
        }
    Registries.Component.extend(AbstractReceiptScreen, PosResAbstractReceiptScreen);

    // Inherit OrderReceipt
    const PosResOrderReceipt = (OrderReceipt) =>
        class extends OrderReceipt{


            constructor() {
                super(...arguments);
                var self = this;

                 async function doTask(imgUrl){
                        var fullurl='/report/ajaxqr/?value='+ imgUrl;
                        var result='';
                          await $.ajax({
                                type: "GET",
                                url: fullurl,
                                success: function(response){
                                    result= response;
                                }
                        });
                        return result;
                    }


                setTimeout( async function(){
                    if(self.env.pos.config.use_custom_receipt){


                        var receipt_design_id = self.env.pos.config.receipt_design_id[0]
                        var receipt_design = self.env.pos.db.receipt_by_id[receipt_design_id].receipt_design
                        var order = self.env.pos.get_order();
                        var companyname =order.export_for_printing().company.name;
                        var companyvat =order.export_for_printing().company.vat;
                        var orderdate=order.export_for_printing().date.localestring;
                        var ordertotalincl=order.export_for_printing().total_with_tax;
                        var ordertax=order.export_for_printing().total_tax;
                        var qrcodedata=companyname +' '+ companyvat +' '+ orderdate +' '+ ordertotalincl.toFixed(2) +' '+ ordertax.toFixed(2) ;

                var  qrcodeimg = await  doTask(qrcodedata);


                        if(!qrcodeimg){

                               console.log('not qrcodeimg');

                            }
                            else {
                            qrcodeimg ='data:image/png;base64,' + qrcodeimg ;
                            }

                        var data = { widget: self.env,
                            pos: order.pos,
                            order: order,
                            receipt: order.export_for_printing(),
                            orderlines: order.get_orderlines(),
                            qrcode :qrcodedata,
                            qrcodeimg :qrcodeimg,
                            paymentlines: order.get_paymentlines(), };
                        var parser = new DOMParser();
                        var xmlDoc = parser.parseFromString(receipt_design,"text/xml");

                        var s = new XMLSerializer();
                        var newXmlStr = s.serializeToString(xmlDoc);

                        //Works using the DOMParser
                        var qweb = new QWeb2.Engine();
                        qweb.add_template('<templates><t t-name="receipt_design">'+newXmlStr+'</t></templates>');

                        var receipt = qweb.render('receipt_design',data) ;
                        $('div.pos-receipt').replaceWith(receipt);
                    }
                },1000);
            }

        }
    Registries.Component.extend(OrderReceipt, PosResOrderReceipt);
});