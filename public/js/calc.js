function allChanged() {
	try {
		for (var i = 0; i < 100; ++i)
			quantityChanged("id_work_set-" + i + "-quantity");
	} catch (e){}
}
function quantityChanged(elem_id) {
	var id = elem_id.split('-')[1];
	for (var i = 0; i < prices.length; ++i) {
		if (
			document.getElementById("id_work_set-" + id + "-executor_status").value == prices[i]['executor_status_id'] &&
			document.getElementById("id_payment_method").value == prices[i]['payment_method_id'] &&
			document.getElementById("id_branch").value == prices[i]['branch_id'] &&
			document.getElementById("id_service").value == prices[i]['service_id']
			) {
				document.getElementById("id_work_set-" + id + "-total").setAttribute("value", (parseFloat(prices[i]['cost']) * parseFloat(document.getElementById("id_work_set-" + id + "-quantity").value)).toFixed(2));
				totalChanged(elem_id);
			}
	}
}
function totalChanged(elem_id) {
	var id = elem_id.split('-')[1];
	for (var i = 0; i < prices.length; ++i) {
		if (
			document.getElementById("id_work_set-" + id + "-executor_status").value == prices[i]['executor_status_id'] &&
			document.getElementById("id_payment_method").value == prices[i]['payment_method_id'] &&
			document.getElementById("id_branch").value == prices[i]['branch_id'] &&
			document.getElementById("id_service").value == prices[i]['service_id']
			) {
				document.getElementById("id_work_set-" + id + "-broker_sum").setAttribute("value", (document.getElementById("id_work_set-" + id + "-total").value * prices[i]['broker_percent'] / 100.0).toFixed(2));
				document.getElementById("id_work_set-" + id + "-executor_sum").setAttribute("value", (document.getElementById("id_work_set-" + id + "-total").value * prices[i]['executor_percent'] / 100.0).toFixed(2));
				for (var j = 0; j < payment_methods.length; ++j) {
					if (document.getElementById("id_payment_method").value == payment_methods[j]['id']) {
						if (payment_methods[j]['broker_multiplyer'].toString() == "1") {
							document.getElementById("id_work_set-" + id + "-broker_balance").setAttribute("value", (document.getElementById("id_work_set-" + id + "-total").value - document.getElementById("id_work_set-" + id + "-broker_sum").value).toFixed(2));
						} else {
							document.getElementById("id_work_set-" + id + "-broker_balance").setAttribute("value", (-document.getElementById("id_work_set-" + id + "-broker_sum").value)).toFixed(2);
						}
						if (parseFloat(payment_methods[j]['executor_multiplyer'].toString()) == 1.0) {
							document.getElementById("id_work_set-" + id + "-executor_balance").setAttribute("value",  (document.getElementById("id_work_set-" + id + "-total").value - document.getElementById("id_work_set-" + id + "-executor_sum").value).toFixed(2));
						} else {
							document.getElementById("id_work_set-" + id + "-executor_balance").setAttribute("value", (-document.getElementById("id_work_set-" + id + "-executor_sum").value).toFixed(2));
						}
					}
				}
		}
	}
}
