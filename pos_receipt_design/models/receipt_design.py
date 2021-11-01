from odoo import api, fields, models, _


class ReceiptDesign(models.Model):
    _name = "receipt.design"
    _rec_name = "name"

    name = fields.Char(string="Name")
    receipt_design = fields.Text(string='Description', required=True)

    @api.model
    def _create_receipt_design_1(self):
        record_data = {}
        record_data['name'] = "Receipt Design 1"
        record_data['receipt_design'] = """ 

   <div class="pos-receipt" style="direction:rtl;">

            <t t-if='receipt.company.logo'>
                <img style="width: 30%;display: block;margin: auto;" t-att-src='receipt.company.logo' alt="Logo"/>
                <br/>
            </t>
            <div style="font-size: 90%; text-align:center;">

                    <h2 class="pos-receipt-center-align">
                        <t t-esc='receipt.company.name' />
                    </h2>

                <t t-if='receipt.header_html'>
                    <t t-raw='receipt.header_html' />
                </t>
                <t t-if='!receipt.header_html and receipt.header'>
                    <div><t t-esc='receipt.header' /></div>
                </t>

                 <t t-if='receipt.company.vat'>
                    <div>الرقم الضريبي :<t t-esc='receipt.company.vat' /></div>
                </t>           


            </div>
             <br/>
            <div style="text-align:center;">
             <span>
               <t t-esc='receipt.company.name' />
            ترحب بكم
             </span>
            </div>
            <br/>
            <!-- Orderlines -->
            <div class='orderlines'>
                <div style="font-weight: bolder;text-align:center; font-size: 90%; border-top: 3px dashed black;border-bottom: 3px dashed black;padding-top: 5px;padding-bottom: 5px;">
                    <div> 
                    الفاتورة :
                    <span t-esc='receipt.name' />
                    </div>
                    <br/>
                    <div> 
                    التاريخ :
                    <t t-if='receipt.date.localestring ' >
                     <span t-esc='receipt.date.localestring' />
                     </t>
                    <t t-else='' >
                    <span t-esc='order.validation_date' />
                    </t>
                    </div>
                    <br/>
                    <t t-if='receipt.client'>
                        <div> 
                        العميل :

                        <t t-esc='receipt.client.name' />
                        </div>
                        <br/>
                    </t>
                    <t t-if='receipt.cashier'>
                    <div class='cashier'>
                        <div>
                        البائع :
                           <t t-esc='receipt.cashier' />
                        </div>
                    </div>
                    </t>

                    </div>
                    <br/>

                    <table style="width: 100%;font-weight: bolder;">
                        <tr style="font-weight: bolder;border-bottom: 2px solid black;font-size:13px;">
                        <th style="text-align:right;">المنتج</th>
                        <th  style="text-align:right;">الكمية</th>
                        <th style="text-align: center;">سعر الوحده </th>
                        <th>الاجمالي</th>
                        <th>الضريبة 15%</th>
                        <th>الاجمالي</th>
                        </tr>
                        <t t-set="discountlist" t-value="0" />
                        <t t-set="linepriceafterdesc" t-value="0" />
                        <tr t-foreach="receipt.orderlines" t-as="line" style="font-weight: bolder;border-bottom: 3px solid #ddd;font-size:70%;">
                        <t t-set="linetaxamount" t-value="0" />
                        <td style="padding-right: 2px;border:1px solid #ddd;"><div style="text-align: right;padding-top: 10px;padding-bottom: 10px;">
                           <!-- <span style="text-align: right;" t-esc='line.product_name_wrapped[0]'/>-->
                               <span style="text-align: right;" t-esc='line.product_name'/>

                            </div>
                        </td>
                        <td style="border:1px solid #ddd;text-align: center;"><span t-esc="line.quantity"/></td>
                        <td style="padding-right: 2px;border:1px solid #ddd;text-align: right;">
                          <div style="padding-top: 10px;padding-bottom: 10px;">

<span t-esc="widget.pos.format_currency_no_symbol(line.price_lst)" />
                    <t t-if=" line.price != line.price_lst">
                        <t t-set="discountlist" t-value="(line.price_lst - line.price) + discountlist" />
                        <t t-set="discountlinerate" t-value="0" />
                        <t t-set="discountlinerate" t-value="Math.round(((line.price_lst - line.price) / line.price_lst ) * 100 )" />
                               <t t-if="discountlinerate > 0">
                                <h5 style="font-weight: bolder;text-align: right;margin-top: 0%;margin-bottom: 0%;font-size: 85%;color: #848484;">
                                   تخفيض <span t-esc='discountlinerate' t-options='{"widget": "float", "precision": 2}' />%
                                </h5>
                            <span t-esc="widget.pos.format_currency_no_symbol(line.price)" />
                            </t>

                    </t>


                            <t t-if='line.discount !== 0'>
                                <h5 style="text-align: right;margin-top: 0%;margin-bottom: 0%;font-size: 85%;color: #848484;">
                                 الخصم <span t-esc='line.discount' />%
                                </h5>
                                <t t-set="linepriceafterdesc" t-value="(line.price - (line.discount / 100 ) * line.price)" />
                                 <span t-esc="widget.pos.format_currency_no_symbol(linepriceafterdesc)" />
                            </t>
                            </div>


                          </td>
                        <td style="padding-right: 2px;border:1px solid #ddd;text-align: right;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_without_tax)'/></td>
                        <td style="padding-right: 2px;border:1px solid #ddd;text-align: right;">
                          <span t-esc='widget.pos.format_currency_no_symbol(line.tax)'/>
                          </td>
                        <td style="padding-right: 2px;border:1px solid #ddd;text-align: right;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_with_tax)'/></td>

                        </tr>
                    </table>
                </div>
            <div>
            <!-- Subtotal -->
            <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
            <t t-if='!taxincluded'>
                <br/> 
                <div style="padding-bottom: 4px;text-align: left; font-weight: bolder; font-size: 15px;border-top: 2px solid; padding-top: 2%;">
                  <span style="text-align: right;float: inline-start;float: right;"> 
                  الاجمالي الفرعي : 
                   </span> 
                  <span t-esc='widget.pos.format_currency(receipt.subtotal)' class=""/>
                  </div>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-weight: bolder;text-align: left; font-size: 15px;border-top: 2px solid; padding-top:2%;">
                      <span style="text-align: right;float: inline-start;float: right;"> 
                        <t t-esc='tax.name' />
                        </span> 
                        <span t-esc='widget.pos.format_currency(tax.amount)' class=""/>
                    </div>
                </t>
          <br/>
         </t>
            <!-- Total -->

                        <!-- Extra Payment Info -->
            <t t-if='receipt.total_discount or discountlist '>
                <div style="font-weight: bolder;text-align: left;font-size: 15px;border-top: 1px solid;padding-top: 2%;">
                  <span style="text-align: right;float: inline-start;float: right;"> 
                    اجمالي الخصم :
                    </span> 
                    <t t-set="discountlist" t-value="discountlist + receipt.total_discount "/>
                    <span style="" t-esc='widget.pos.format_currency(discountlist)'/>
                </div>
             <br/>
           </t>

            <div style="font-weight: bolder;text-align: left;font-size: 15px; border-top: 2px solid;padding-top: 2%;">
                  <span style="text-align: right;float: inline-start;float: right;"> 
                  الاجمالي :
                  </span> 
                <span style="" t-esc='widget.pos.format_currency(receipt.total_with_tax)'/>
            </div>
            <br/>
            <t t-if='taxincluded'>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-weight: bolder;text-align: left;display:none;font-size: 15px; font-weight: 700; border-top: 1px solid;padding-top: 2%;">
                        <span style="text-align: right;float: inline-start;float: right;">
                        <t t-esc='tax.name' />
                        </span>
                        <span t-esc='widget.pos.format_currency(tax.amount)'/>

                    </div>
                </t>
                <div style="font-weight: bolder;text-align: left;font-size: 15px; font-weight: 700;">
                  <span style="text-align: right;float: inline-start;float: right;"> 
                    اجمالي الضريبة :
                    </span>

                    <span  style="" t-esc='widget.pos.format_currency(receipt.total_tax)'/>
                </div>
                 <br/>
            </t>
            </div>


            <div style="font-weight: bolder;border-top: 1px dashed black;padding-top: 5%;border-bottom: 1px dashed black;">
                <!-- Payment Lines -->
                <t t-foreach='paymentlines' t-as='line'>
                    <div style="font-weight: bolder;text-align: left;font-size: 15px;">
                      <span style="text-align: right;float: inline-start;float: right;"> 
                        <t t-esc='line.name' />
                         </span>
                        <span style=""  t-esc='widget.pos.format_currency(line.get_amount())' class=""/>
                    </div>
                </t>
                <br/>
                <div  class="receipt-change" style="font-weight: bolder;text-align: left;font-size: 15px;">
                  <span style="text-align: right;float: inline-start;float: right;">
                    المتبقي
                     </span>

                    <span style="" t-esc='widget.pos.format_currency(receipt.change)' class=""/>
                </div>
                <br/>
            </div>
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html'  class="pos-receipt-center-align" style="font-weight: bolder;font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer'  class="pos-receipt-center-align" style="font-weight: bolder;font-size: 14px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/>

            </div>
            <div class='after-footer' style="font-size: 14px;">
                <t t-foreach='paymentlines' t-as='line'>
                    <t t-if='line.ticket'>
                        <br />
                        <div class="pos-payment-terminal-receipt">
                            <t t-raw='line.ticket'/>
                        </div>
                    </t>
                </t>
            </div>
            <br/>
            <t t-if='qrcode'>
            <div style="text-align:center;">
                <t t-if='qrcodeimg' >
                 <t t-set='qrcodegenerate' t-value='qrcodeimg'/>
                </t>
                <t t-else=''>
                  <t t-set='qrcodegenerate' >/report/qr/?value=<t t-esc='qrcode' /></t>
              </t>
            <img t-att-src='qrcodegenerate' style="width:100;height:100"/>

            </div>
             </t>


        </div>
                """
        record_id = self.create(record_data)
        pos_config_id = self.env.ref('point_of_sale.pos_config_main')
        if record_id and pos_config_id:
            pos_config_id.use_custom_receipt = True
            pos_config_id.receipt_design_id = record_id.id
