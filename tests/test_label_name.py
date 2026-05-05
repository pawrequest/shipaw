from shipaw.utils.label_file import get_label_stem


def test_label_name(
    sample_shipment, sample_remote_fc, sample_shipment_dropoff, sample_shipment_inbound, sample_home_address
):
    assert (
        get_label_stem(sample_shipment)
        == f'Shipping_Label TO {sample_remote_fc.address.business_name} ON {sample_shipment.shipping_date.isoformat()}'.replace(
            ' ', '_'
        )
    )
    assert (
        get_label_stem(sample_shipment_dropoff)
        == f'Dropoff Label FROM {sample_remote_fc.address.business_name} TO {sample_home_address.business_name} ON {sample_shipment_dropoff.shipping_date.isoformat()}'.replace(
            ' ', '_'
        )
    )
    assert (
        get_label_stem(sample_shipment_inbound)
        == f'Shipping Label FROM {sample_remote_fc.address.business_name} TO {sample_home_address.business_name} ON {sample_shipment_dropoff.shipping_date.isoformat()}'.replace(
            ' ', '_'
        )
    )
