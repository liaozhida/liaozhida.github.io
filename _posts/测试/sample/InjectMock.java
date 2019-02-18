package com.alibaba.onetouch.commission;

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.onetouch.commission.api.base.Page;
import com.alibaba.onetouch.commission.bizservice.message.producer.impl.AccountingMessageProducerImpl;
import com.alibaba.onetouch.commission.bizservice.service.accounting.impl.SimpleAccountingServiceImpl;
import com.alibaba.onetouch.commission.bizservice.service.settlement.impl.SettlementBizServiceImpl;
import com.alibaba.onetouch.commission.core.settlement.model.Settlement;
import com.alibaba.onetouch.commission.dal.dataobject.join.SettlementDetailCostDO;
import com.google.common.collect.Lists;
import com.taobao.pandora.boot.test.junit4.DelegateTo;
import com.taobao.pandora.boot.test.junit4.PandoraBootRunner;

@RunWith(PandoraBootRunner.class)
@DelegateTo(MockitoJUnitRunner.class)
public class AccoutingServiceUnitTest {

    @InjectMocks
    private SimpleAccountingServiceImpl   simpleAccountingService;

    @Mock
    private SettlementBizServiceImpl      settlementBizService;

    @Mock
    private AccountingMessageProducerImpl accountingMessageProducer;

    private final Long                    paymentId = 14377L;
    private final String                  fpmNo     = "JS0000093443";

    @Before
    public void setUp() throws Exception {

        Page<Settlement> settlementPage = new Page<Settlement>();
        Settlement settlement = new Settlement();
        settlement.setId(1L);
        settlement.setSupplierId(2L);
        List<Settlement> records = Lists.newArrayList();
        records.add(settlement);
        settlementPage.setRecords(records);
        when(settlementBizService.querySupplierSettlement(any())).thenReturn(settlementPage);

        List<SettlementDetailCostDO> settlementDetailCostDOList = Lists.newArrayList();
        SettlementDetailCostDO settlementDetailCostDO = new SettlementDetailCostDO();
        settlementDetailCostDO.setCostId(3L);
        settlementDetailCostDOList.add(settlementDetailCostDO);
        when(settlementBizService.queryDetailCostBySettlementId(settlement.getId())).thenReturn(settlementDetailCostDOList);
    }

    @Test
    public void execute() {
        simpleAccountingService.sendAccountingMsg(paymentId, fpmNo);
    }

    @Test
    public void jsonTest() {
        String str = "{\"fpmNo\":\"JS0000252247\",\"id\":262226,\"resultURL\":\"https://wallstreet.alibaba-inc.com/paycenter/fpm/orderDetail.htm?headerId=262226\"}";
        JSONObject json = JSON.parseObject(str);
        String fpmNo = json.get("fpmNo").toString();
        assertEquals("JS0000252247", fpmNo);

    }
}
