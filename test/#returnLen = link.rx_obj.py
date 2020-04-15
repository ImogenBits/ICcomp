                #returnLen = link.rx_obj(int, intSize, receivedBytes)
                #receivedBytes += intSize
                #returnPageNum = link.rx_obj(int, intSize, receivedBytes)
                #receivedBytes += intSize
                #returnArray = link.rx_obj(list, returnLen, receivedBytes, "B")
                #
                #print("SENT page {}, {} bytes: {}".format(pageNum, arraySize, dataArray.hex(" ")))
                #print("RCVD page {}, {} bytes: {}".format(returnPageNum, returnLen, " ".join([hex(i)[2:] for i in returnArray])))