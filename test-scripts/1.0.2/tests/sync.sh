#!/bin/bash

source ../../export-env-vars.sh

set -ex

UUID=`uuidgen`

echo $FROM_ASID

curl -i --request POST \
--url http://outbound80.fe50331779a548dda05c.ukwest.aksapp.io:80/ \
--header 'content-type: application/json' \
--header 'from-asid: '$FROM_ASID'' \
--header 'interaction-id: QUPA_IN040000UK32' \
--header 'wait-for-response: false' \
--data '{"payload": "<QUPA_IN040000UK32 xmlns=\"urn:hl7-org:v3\" xmlns:hl7=\"urn:hl7-org:v3\">\r\n <id root=\"'$UUID'\" />\r\n <creationTime value=\"20190927152035\" />\r\n <versionCode code=\"V3NPfIT3.0\" />\r\n <interactionId root=\"2.16.840.1.113883.2.1.3.2.4.12\" extension=\"QUPA_IN040000UK32\" />\r\n <processingCode code=\"P\" />\r\n <processingModeCode code=\"T\" />\r\n <acceptAckCode code=\"NE\" />\r\n <communicationFunctionRcv>\r\n <device classCode=\"DEV\" determinerCode=\"INSTANCE\">\r\n <hl7:id xmlns:SOAP=\"http://schemas.xmlsoap.org/soap/envelope/\" extension=\"928942012545\" root=\"1.2.826.0.1285.0.2.0.107\" />\r\n </device>\r\n </communicationFunctionRcv>\r\n <communicationFunctionSnd>\r\n <device classCode=\"DEV\" determinerCode=\"INSTANCE\">\r\n <hl7:id xmlns:SOAP=\"http://schemas.xmlsoap.org/soap/envelope/\" extension=\"918999198982\" root=\"1.2.826.0.1285.0.2.0.107\" />\r\n </device>\r\n </communicationFunctionSnd>\r\n <ControlActEvent classCode=\"CACT\" moodCode=\"EVN\">\r\n <author1 typeCode=\"AUT\">\r\n <AgentSystemSDS classCode=\"AGNT\">\r\n <agentSystemSDS classCode=\"DEV\" determinerCode=\"INSTANCE\">\r\n <hl7:id xmlns:SOAP=\"http://schemas.xmlsoap.org/soap/envelope/\" extension=\"918999198982\" root=\"1.2.826.0.1285.0.2.0.107\" />\r\n </agentSystemSDS>\r\n </AgentSystemSDS>\r\n </author1>\r\n <query>\r\n <historicDataIndicator>\r\n <value code=\"0\" codeSystem=\"2.16.840.1.113883.2.1.3.2.4.17.36\" />\r\n <semanticsText>historicDataIndicator</semanticsText>\r\n </historicDataIndicator>\r\n <person.id>\r\n <value root=\"2.16.840.1.113883.2.1.4.1\" extension=\"9689174606\" />\r\n <semanticsText>person.id</semanticsText>\r\n </person.id>\r\n <retrievalItem>\r\n <semanticsText>person.allData</semanticsText>\r\n </retrievalItem>\r\n </query>\r\n </ControlActEvent>\r\n </QUPA_IN040000UK32>"}'
