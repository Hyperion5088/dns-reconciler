from custom_components.dns_reconciler.coordinator import should_auto_reconcile


def test_auto_reconcile_only_when_enabled_and_out_of_sync():
    assert should_auto_reconcile(True, "217.43.36.165", "1.2.3.4") is True
    assert should_auto_reconcile(True, "217.43.36.165", "217.43.36.165") is False
    assert should_auto_reconcile(False, "217.43.36.165", "1.2.3.4") is False
    assert should_auto_reconcile(True, None, "1.2.3.4") is False
