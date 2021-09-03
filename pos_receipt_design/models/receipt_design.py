
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
            <br/>
            <t t-if='receipt.company.logo'>
                <img style="width: 30%;display: block;margin: auto;" t-att-src='receipt.company.logo' alt="Logo"/>
                <br/>
            </t>
            <div style="font-size: 80%; text-align:center;">
               
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

                <br/>
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
                <div style="text-align:center; font-size: 75%; border-top: 1px dashed black;border-bottom: 1px dashed black;padding-top: 5px;padding-bottom: 5px;">
                    <div> 
                    الفاتورة :
                    <span t-esc='receipt.name' />
                    </div>
                    <br/>
                    <div> 
                    التاريخ :
                    <span t-esc='receipt.date.localestring' />
                    </div>
                    <br/>
                    <t t-if='receipt.client'>
                        <div> 
                        العميل :

                        <t t-esc='receipt.client' />
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
                    <br/>
                    <table style="width: 100%;">
                        <tr style="border-bottom: 2px solid black;font-size:15px;">
                        <th style="text-align:right;">المنتج</th>
                        <th  style="text-align:right;">الكمية</th>
                        <th style="text-align: center;">سعر الوحده </th>
                        <th>الاجمالي</th>
                        <th>الضريبة 15%</th>
                        <th>الاجمالي</th>
                        </tr>
                        <t t-set="discountlist" t-value="0" />
                        <t t-set="linepriceafterdesc" t-value="0" />
                        <tr t-foreach="receipt.orderlines" t-as="line" style="border-bottom: 1px solid #ddd;font-size: 16px;font-family: initial;">
                        <t t-set="linetaxamount" t-value="0" />
                        <td><div style="text-align: right;padding-top: 10px;padding-bottom: 10px;">
                            <span style="text-align: right;" t-esc='line.product_name_wrapped[0]'/>
                            
                            </div>
                        </td>
                        <td style="text-align: center;"><span t-esc="line.quantity"/></td>
                        <td style="text-align: center;">
                          <div style="padding-top: 10px;padding-bottom: 10px;">
                        
                    <t t-if=" line.price != line.price_lst">
                        <t t-set="discountlist" t-value="" />
                            <span t-esc="widget.pos.format_currency_no_symbol(line.price_lst)" />
                                <h5 style="text-align: right;margin-top: 0%;margin-bottom: 0%;font-size: 9px;color: #848484;">
                                    <span t-esc='widget.pos.default_pricelist.name' />
                                </h5>
                            <span t-esc="widget.pos.format_currency_no_symbol(line.price)" />
                            
                    
                    </t>
                    
                    <t t-elif="line.discount !== 0">
                        
                            <t t-if="widget.pos.config.iface_tax_included == 'total'">
                                <span t-esc="widget.pos.format_currency_no_symbol(line.price_with_tax_before_discount)"/>
                            </t>
                            
                            <t t-else="">
                                <span t-esc="widget.pos.format_currency_no_symbol(line.price)"/>
                            </t>
                       
                    </t>
                    
                            <t t-if='line.discount !== 0'>
                                <h5 style="text-align: right;margin-top: 0%;margin-bottom: 0%;font-size: 9px;color: #848484;">
                                 الخصم <span t-esc='line.discount' />%
                                </h5>
                                <t t-set="linepriceafterdesc" t-value="(line.price - (line.discount / 100 ) * line.price)" />
                                 <span t-esc="widget.pos.format_currency_no_symbol(linepriceafterdesc)" />
                            </t>
                            </div>
                          
                          
                          </td>
                        <td style="text-align: center;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_without_tax)'/></td>
                        <td style="text-align: center;">
                          <span t-esc='widget.pos.format_currency_no_symbol(line.tax)'/>
                          </td>
                        <td style="text-align: center;"><span t-esc='widget.pos.format_currency_no_symbol(line.price_with_tax)'/></td>

                        </tr>
                    </table>
                </div>
            <div>
            <!-- Subtotal -->
            <t t-set='taxincluded' t-value='Math.abs(receipt.subtotal - receipt.total_with_tax) &lt;= 0.000001' />
            <t t-if='!taxincluded'>
                <br/> 
                <div style="font-weight: 700; font-size: 20px;border-top: 2px solid; padding-top: 2%;">
                  <span style="text-align: right;float: inline-start;"> 
                  الاجمالي الفرعي : 
                   </span> 
                  <span t-esc='widget.pos.format_currency(receipt.subtotal)' class=""/>
                  </div>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="font-weight: 700;">
                      <span style="text-align: right;float: inline-start;"> 
                        <t t-esc='tax.name' />
                        </span> 
                        <span t-esc='widget.pos.format_currency(tax.amount)' class=""/>
                    </div>
                </t>
            </t>
            <!-- Total -->
            <br/>
                        <!-- Extra Payment Info -->
            <t t-if='receipt.total_discount or discountlist '>
                <div style="font-size: 18px;border-top: 1px solid;padding-top: 2%;">
                  <span style="text-align: right;float: inline-start;"> 
                    اجمالي الخصم :
                    </span> 
                    <t t-set="discountlist" t-value="discountlist + receipt.total_discount "/>
                    <span style="" t-esc='widget.pos.format_currency(discountlist)'/>
                </div>
            </t>
            <br/>
            <div style="font-size: 20px;font-weight: 700; border-top: 2px solid;padding-top: 2%;">
                  <span style="text-align: right;float: inline-start;"> 
                  الاجمالي :
                  </span> 
                <span style="" t-esc='widget.pos.format_currency(receipt.total_with_tax)'/>
            </div>
            <br/>

            
            <t t-if='taxincluded'>
                <t t-foreach='receipt.tax_details' t-as='tax'>
                    <div style="display:none;font-size: 15px; font-weight: 700; border-top: 1px solid;padding-top: 2%;">
                        <span style="text-align: right;float: inline-start;">
                        <t t-esc='tax.name' />
                        </span>
                        <span t-esc='widget.pos.format_currency(tax.amount)'/>
                        
                    </div>
                </t>
                <div style="font-size: 15px; font-weight: 700;">
                  <span style="text-align: right;float: inline-start;"> 
                    اجمالي الضريبة :
                    </span>
                    
                    <span  style="" t-esc='widget.pos.format_currency(receipt.total_tax)'/>
                </div>
            </t>
            </div>
            <br/>
            <br/>
            <div style="border-top: 1px dashed black;padding-top: 5%;border-bottom: 1px dashed black;">
                <!-- Payment Lines -->
                <t t-foreach='paymentlines' t-as='line'>
                    <div style="font-size: 14px;">
                      <span style="text-align: right;float: inline-start;"> 
                        <t t-esc='line.name' />
                         </span>
                        <span style=""  t-esc='widget.pos.format_currency(line.get_amount())' class=""/>
                    </div>
                </t>
                <br/>
                <div  class="receipt-change" style="font-size: 14px;">
                  <span style="text-align: right;float: inline-start;">
                    المتبقي
                     </span>
                    
                    <span style="" t-esc='widget.pos.format_currency(receipt.change)' class=""/>
                </div>
                <br/>
            </div>
            <div class='before-footer' />
            <!-- Footer -->
            <div t-if='receipt.footer_html'  class="pos-receipt-center-align" style="font-size: 14px;">
                <t t-raw='receipt.footer_html'/>
            </div>
            <div t-if='!receipt.footer_html and receipt.footer'  class="pos-receipt-center-align" style="font-size: 13px;">
                <br/>
                <t t-esc='receipt.footer'/>
                <br/>
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
              <t t-set='qrcodegenerate' >/report/qr/?value=<t t-esc='qrcode' /></t>
            <img t-att-src='qrcodegenerate' style="width:100;height:100"/>
           
            </div>
             </t>
              <br/>

        </div>
                """
        record_id = self.create(record_data)
        pos_config_id = self.env.ref('point_of_sale.pos_config_main')
        if record_id and pos_config_id:
            pos_config_id.use_custom_receipt = True
            pos_config_id.receipt_design_id = record_id.id