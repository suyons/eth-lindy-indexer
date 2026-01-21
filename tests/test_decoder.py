from domain.decoder import LogDecoder


def test_decode_transfer_log_success():
    decoder = LogDecoder()

    raw_log = {
        "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x000000000000000000000000d8da6bf26964af9d7eed9e03e53415d37aa96045",
            "0x0000000000000000000000001234567890123456789012345678901234567890",
        ],
        "data": "0x0000000000000000000000000000000000000000000000000de0b6b3a7640000",  # 1e18
        "transactionHash": "0x" + "1" * 64,
        "transactionIndex": 0,
        "blockNumber": 12345,
        "logIndex": 0,
        "address": "0x" + "a" * 40,
    }

    event = decoder.decode_transfer_log(raw_log)

    assert event is not None
    assert event.from_address == "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
    assert event.to_address == "0x1234567890123456789012345678901234567890"
    assert event.value == 10**18
    assert event.block_number == 12345


def test_decode_transfer_log_invalid_topic():
    decoder = LogDecoder()

    raw_log = {
        "topics": ["0x" + "0" * 64],
        "data": "0x",
        "transactionHash": "0x" + "1" * 64,
        "blockNumber": 12345,
        "logIndex": 0,
    }

    event = decoder.decode_transfer_log(raw_log)
    assert event is None


def test_decode_batch():
    decoder = LogDecoder()
    logs = [
        {
            "topics": [
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "0x000000000000000000000000d8da6bf26964af9d7eed9e03e53415d37aa96045",
                "0x0000000000000000000000001234567890123456789012345678901234567890",
            ],
            "data": "0x000000000000000000000000000000000000000000000000000000000000000a",
            "transactionHash": "0x" + "1" * 64,
            "blockNumber": 12345,
            "logIndex": 0,
        },
        {"topics": ["0x" + "0" * 64], "data": "0x"},
    ]

    events = decoder.decode_batch(logs)
    assert len(events) == 1
    assert events[0].value == 10
