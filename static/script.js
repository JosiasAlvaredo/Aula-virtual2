
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  try {
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) throw new Error("Error en la petición");

    const data = await res.json();

    if (data.success) {
      localStorage.setItem("loggedIn", "true");
      window.location.href = "index.html";
    } else {
      alert("Usuario o contraseña incorrectos");
    }
  } catch (error) {
    console.error(error);
    alert("Error en el servidor");
  }
});

document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("registerEmail").value;
  const password = document.getElementById("registerPassword").value;

  try {
    const res = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) throw new Error("Error en la petición");

    const data = await res.json();

    if (data.success) {
      localStorage.setItem("loggedIn", "true"); 
      window.location.href = "index.html"; 
    } else {
      alert("Error al registrar el usuario");
    }
  } catch (error) {
    console.error(error);
    alert("Error en el servidor");
  }
});

if (window.location.pathname.includes("index.html")) {
  if (!localStorage.getItem("loggedIn")) {
    window.location.href = "login.html";
  }
}

document.getElementById("logoutBtn")?.addEventListener("click", () => {
  localStorage.removeItem("loggedIn");
  window.location.href = "login.html";
});
