/* ============================================================
   LUXE FASHION — Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Navbar scroll effect ─────────────────────────────────
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 30);
    });
  }

  // ── Auto-dismiss toasts ──────────────────────────────────
  document.querySelectorAll('.toast').forEach(toast => {
    setTimeout(() => {
      const bsToast = bootstrap.Toast.getInstance(toast) || new bootstrap.Toast(toast, { delay: 4000 });
      bsToast.hide();
    }, 4000);
  });

  // ── Search suggestions ───────────────────────────────────
  const searchInput = document.getElementById('searchInput');
  const suggestionsBox = document.getElementById('searchSuggestions');
  let searchTimer;

  if (searchInput && suggestionsBox) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimer);
      const q = this.value.trim();
      if (q.length < 2) {
        suggestionsBox.style.display = 'none';
        return;
      }
      searchTimer = setTimeout(() => {
        fetch(`/api/search-suggestions?q=${encodeURIComponent(q)}`)
          .then(r => r.json())
          .then(data => {
            if (!data.length) { suggestionsBox.style.display = 'none'; return; }
            suggestionsBox.innerHTML = data.map(item =>
              `<div class="search-suggestion-item" onclick="selectSuggestion('${item.name}')">
                <strong>${item.name}</strong>
                <span style="color:#aaa;font-size:11px;margin-left:6px">${item.brand}</span>
              </div>`
            ).join('');
            suggestionsBox.style.display = 'block';
          }).catch(() => { suggestionsBox.style.display = 'none'; });
      }, 250);
    });

    document.addEventListener('click', e => {
      if (!searchInput.contains(e.target)) suggestionsBox.style.display = 'none';
    });
  }

  // ── Size selector ────────────────────────────────────────
  document.querySelectorAll('.size-opt').forEach(opt => {
    opt.addEventListener('click', function () {
      const siblings = this.closest('.size-selector').querySelectorAll('.size-opt');
      siblings.forEach(s => s.classList.remove('selected'));
      this.classList.add('selected');
    });
  });

  // ── Product image gallery ────────────────────────────────
  document.querySelectorAll('.product-thumb').forEach(thumb => {
    thumb.addEventListener('click', function () {
      const img = this.querySelector('img').src;
      const main = document.getElementById('mainImg');
      if (main) {
        main.style.opacity = '0';
        setTimeout(() => { main.src = img; main.style.opacity = '1'; }, 150);
      }
      document.querySelectorAll('.product-thumb').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // ── Review star rating ───────────────────────────────────
  const stars = document.querySelectorAll('.review-stars input');
  stars.forEach(star => {
    star.addEventListener('change', function () {
      const val = parseInt(this.value);
      stars.forEach(s => {
        s.nextElementSibling.style.color = parseInt(s.value) >= val ? '#f59e0b' : '#ddd';
      });
    });
  });

  // ── Cart AJAX add ────────────────────────────────────────
  const cartForm = document.getElementById('addToCartForm');
  if (cartForm) {
    cartForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = this.querySelector('button[type="submit"]');
      btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Adding...';
      btn.disabled = true;

      fetch(this.action, {
        method: 'POST',
        body: new FormData(this),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(r => r.json())
        .then(data => {
          showToast(data.message, data.success ? 'success' : 'error');
          if (data.success) {
            // Update cart count
            const badge = document.querySelector('.cart-badge');
            if (badge) badge.textContent = data.count;
            else if (data.count > 0) {
              const cartIcon = document.querySelector('a[href*="/cart"] .nav-icon');
              // Re-render badge on next navigation
            }
          }
        })
        .catch(() => showToast('Something went wrong.', 'error'))
        .finally(() => {
          btn.innerHTML = '<i class="fas fa-shopping-bag me-2"></i> Add to Cart';
          btn.disabled = false;
        });
    });
  }

  // ── Lazy loading images ──────────────────────────────────
  if ('IntersectionObserver' in window) {
    const imgObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            imgObserver.unobserve(img);
          }
        }
      });
    }, { rootMargin: '50px' });
    document.querySelectorAll('img[data-src]').forEach(img => imgObserver.observe(img));
  }

});

// ── Helper functions ─────────────────────────────────────

function selectSuggestion(name) {
  const input = document.getElementById('searchInput');
  const suggestions = document.getElementById('searchSuggestions');
  if (input) input.value = name;
  if (suggestions) suggestions.style.display = 'none';
  input.closest('form').submit();
}

function showToast(message, type = 'success') {
  const container = document.querySelector('.toast-container') ||
    (() => {
      const c = document.createElement('div');
      c.className = 'toast-container position-fixed top-0 end-0 p-3';
      c.style.zIndex = '1100';
      document.body.appendChild(c);
      return c;
    })();

  const iconMap = {
    success: 'fa-check-circle text-success',
    error: 'fa-exclamation-circle text-danger',
    info: 'fa-info-circle text-info',
    warning: 'fa-exclamation-triangle text-warning',
  };

  const toast = document.createElement('div');
  toast.className = 'toast align-items-center border-0 show';
  toast.style.marginBottom = '8px';
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        <i class="fas ${iconMap[type] || iconMap.info} me-2"></i>${message}
      </div>
      <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  container.appendChild(toast);
  const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
  bsToast.show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function togglePw(inputId, iconId) {
  const inp = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  if (!inp) return;
  inp.type = inp.type === 'password' ? 'text' : 'password';
  if (icon) icon.className = inp.type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
}
