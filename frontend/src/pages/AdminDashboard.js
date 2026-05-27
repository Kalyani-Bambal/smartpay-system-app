import React, {
  useEffect,
  useState
} from "react";

import axios from "axios";

function AdminDashboard() {

  const [transactions, setTransactions] =
    useState([]);

  useEffect(() => {

    fetchData();

  }, []);

  const fetchData = async () => {

    const response = await axios.get(
      "http://localhost:5000/admin/transactions"
    );

    setTransactions(response.data);
  };

  return (

    <div>

      <h1>Admin Dashboard</h1>

      {
        transactions.map((txn) => (

          <div key={txn.id}>

            <p>
              {txn.sender}
              {" → "}
              {txn.receiver}
            </p>

            <p>
              ₹ {txn.amount}
            </p>

            <p>
              {txn.status}
            </p>

            <hr />

          </div>
        ))
      }

    </div>
  );
}

export default AdminDashboard;