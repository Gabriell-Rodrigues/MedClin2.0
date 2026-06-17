/* MedClin — interações de interface (apenas visual/acessibilidade).
   Nenhuma regra de negócio aqui. */

(function () {
  "use strict";

  var THEME_KEY = "medclin-theme";

  function aplicarTema(tema) {
    document.documentElement.setAttribute("data-theme", tema);
    var btn = document.querySelector("[data-theme-toggle]");
    if (btn) {
      var escuro = tema === "dark";
      // Rótulo acessível descreve a ação do clique (não o estado atual).
      btn.setAttribute(
        "aria-label",
        escuro ? "Ativar modo claro" : "Ativar modo escuro"
      );
      btn.setAttribute("title", escuro ? "Ativar modo claro" : "Ativar modo escuro");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    // --- Tema claro/escuro -------------------------------------------------
    var temaAtual =
      document.documentElement.getAttribute("data-theme") || "light";
    aplicarTema(temaAtual);

    var themeToggle = document.querySelector("[data-theme-toggle]");
    if (themeToggle) {
      themeToggle.addEventListener("click", function () {
        var atual =
          document.documentElement.getAttribute("data-theme") === "dark"
            ? "dark"
            : "light";
        var novo = atual === "dark" ? "light" : "dark";
        try {
          localStorage.setItem(THEME_KEY, novo);
        } catch (e) {}
        aplicarTema(novo);
      });
    }

    // --- Menu responsivo ---------------------------------------------------
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector("[data-nav]");

    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", String(open));
      });

      // Fecha o menu ao navegar por teclado para fora (Esc)
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && nav.classList.contains("is-open")) {
          nav.classList.remove("is-open");
          toggle.setAttribute("aria-expanded", "false");
          toggle.focus();
        }
      });
    }
  });
})();
