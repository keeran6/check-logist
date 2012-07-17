function allChanged() {
	try {
		for (var i = 0; i < 100; ++i)
			quantityChanged("id_work_set-" + i + "-quantity");
	} catch (e){}
}

function toggleColor(element) {
	element.style.color = (element.style.color == 'rgb(1, 1, 1)') ? 'black' : '#010101';
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
				document.getElementById("id_work_set-" + id + "-total").value = (prices[i]['cost'] * document.getElementById("id_work_set-" + id + "-quantity").value).toFixed(2);
				toggleColor(document.getElementById("id_work_set-" + id + "-total"));
				totalChanged(elem_id);
				break;
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
				document.getElementById("id_work_set-" + id + "-broker_sum").value = (document.getElementById("id_work_set-" + id + "-total").value * prices[i]['broker_percent'] / 100.0).toFixed(2);
				toggleColor(document.getElementById("id_work_set-" + id + "-broker_sum"));
				document.getElementById("id_work_set-" + id + "-executor_sum").value = (document.getElementById("id_work_set-" + id + "-total").value * prices[i]['executor_percent'] / 100.0).toFixed(2);
				toggleColor(document.getElementById("id_work_set-" + id + "-executor_sum"));
				for (var j = 0; j < payment_methods.length; ++j) {
					if (document.getElementById("id_payment_method").value == payment_methods[j]['id']) {
						if (payment_methods[j]['broker_multiplyer'] == 1) {
							document.getElementById("id_work_set-" + id + "-broker_balance").value = (document.getElementById("id_work_set-" + id + "-total").value - document.getElementById("id_work_set-" + id + "-broker_sum").value).toFixed(2);
						} else {
							document.getElementById("id_work_set-" + id + "-broker_balance").value = (-document.getElementById("id_work_set-" + id + "-broker_sum").value).toFixed(2);
						}
						toggleColor(document.getElementById("id_work_set-" + id + "-broker_balance"));
						if (payment_methods[j]['executor_multiplyer'] == 1) {
							document.getElementById("id_work_set-" + id + "-executor_balance").value = (document.getElementById("id_work_set-" + id + "-total").value - document.getElementById("id_work_set-" + id + "-executor_sum").value).toFixed(2);
						} else {
							document.getElementById("id_work_set-" + id + "-executor_balance").value = (-document.getElementById("id_work_set-" + id + "-executor_sum").value).toFixed(2);
						}
						toggleColor(document.getElementById("id_work_set-" + id + "-executor_balance"));
					}
				}
				break;
		}
	}
}
