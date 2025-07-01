import React, { useState } from "react";
import axios from "axios";

const Signup = () => {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    phone_number: "",
    user_type: "importer_exporter",
  });

  const [responseMsg, setResponseMsg] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:8000/api/v1/user/signup",
        formData
      );
      setResponseMsg("Signup successful!");
      console.log(response.data);
    } catch (error) {
      console.error("Signup error:", error);
      setResponseMsg("Signup failed. Check console for details.");
    }
  };

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#242424",
        color: "#ffffff",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          padding: "24px",
          backgroundColor: "#333",
          borderRadius: "8px",
        }}
      >
        <h2>Signup</h2>

        <label>
          First Name:
          <input
            name="first_name"
            type="text"
            value={formData.first_name}
            onChange={handleChange}
            style={{ padding: "6px", marginTop: "4px" }}
          />
        </label>

        <label>
          Last Name:
          <input
            name="last_name"
            type="text"
            value={formData.last_name}
            onChange={handleChange}
            style={{ padding: "6px", marginTop: "4px" }}
          />
        </label>

        <label>
          Email:
          <input
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            style={{ padding: "6px", marginTop: "4px" }}
          />
        </label>

        <label>
          Password:
          <input
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            style={{ padding: "6px", marginTop: "4px" }}
          />
        </label>

        <label>
          Phone Number:
          <input
            name="phone_number"
            type="tel"
            value={formData.phone_number}
            onChange={handleChange}
            style={{ padding: "6px", marginTop: "4px" }}
          />
        </label>

        <label>
          User Type:
          <select
            name="user_type"
            value={formData.user_type}
            onChange={handleChange}
            style={{ padding: "6px", marginTop: "4px" }}
          >
            <option value="importer_exporter">Importer/Exporter</option>
            <option value="supplier">Supplier</option>
            <option value="super_admin">Super Admin</option>
          </select>
        </label>

        <button
          type="submit"
          style={{
            padding: "8px",
            backgroundColor: "#555",
            color: "#fff",
            border: "none",
            cursor: "pointer",
          }}
        >
          Sign Up
        </button>

        {responseMsg && <p>{responseMsg}</p>}
      </form>
    </div>
  );
};

export default Signup;
