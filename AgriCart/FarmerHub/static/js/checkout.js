// Select the form with the ID paymentForm and adds an event listener to listen for the submit event
// The sync keyword allows the function to handle asynchronous operations like fetching data from the backend
document.getElementById("payform").addEventListener("submit", async function (event) {
    // Preventing Default Form Submission
event.preventDefault();  
if (this.dataset.submitted) {
    return;  // Prevent double submission
}
this.dataset.submitted = true; // Mark as submitted
// Collecting Form Data
let formData = new FormData(this);

try {
    const transactionId = this.getAttribute("data-tid");
    // sends thte collected form data to the confirm endpoint using a POST request.The fetch API is used for this asynchronous request.The wait keyword ensures that the script waits for the response before continuing

   let response = await fetch(`/checkout/`, {
    method: "POST",
    body: formData
});
        // Parsing the JSON Response from the backend into javascript object
        // This is expected to contain order_id which is required for razorpay
    let data = await response.json();
        // Checking if the Order ID is Available
    if (data.order_id) {
        const homeUrl = document.getElementById("payform").getAttribute("data-home-url");
        const cancelUrl = document.getElementById('payform').getAttribute('data-cancel-url');
            // Configuring Razorpay Payment Options
        var options = {
             // currently key is test key_id
            "key": "rzp_test_fCVgGqgcfDm0Lh",
            "amount": parseInt(data.price),
            "currency": "INR",
            "order_id": data.order_id,
            "name": "store",
            "description": "Booking",
            "prefill": {
                // "name": "{{ data.lres.user.first_name }}",
                // "email": "{{ data.res.user.email }}"
            },
            "theme": { "color": "#F37254" },
            // handling successful Payment
            "handler": async function (response) {
                alert("Payment successful! Payment ID: " + response.razorpay_payment_id);
                 // Send confirmation to the backend
                let confirmResponse = await fetch(`/payment_success/${transactionId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        payment_id: response.razorpay_payment_id,
                        order_id: data.order_id
                    })
                });
                // Handling Backend Confirmation Response
                let confirmData = await confirmResponse.json();
                if (confirmData.status === "success") {
                    window.location.href = homeUrl;;
                } else {
                    alert("Error finalizing order. Please contact support.");
                }
            },
             // Handling Payment Cancellation
            "modal": {
                        "escape": false,
                        "ondismiss": function () {
                            alert("Payment was not completed. Redirecting to cart...");
                            window.location.href =
                                cancelUrl; // Redirect to the cart page
                        }
                    }
        };
            // initializing and opening razorpay payment
            // create a new razorpay instance with the configured options
            // opens the razorpay payment window
        var rzp1 = new Razorpay(options);
        rzp1.open();
    }
} catch (error) {
    console.error("Error processing payment:", error);
}
});