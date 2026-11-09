// NyumbaHub - Main JS

// Sticky navbar shadow on scroll
window.addEventListener('scroll', () => {
  const nav = document.getElementById('navbar');
  if (nav) {
    if (window.scrollY > 50) {
      nav.classList.add('shadow-md');
    } else {
      nav.classList.remove('shadow-md');
    }
  }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Price range formatter
function formatPrice(input) {
  let val = input.value.replace(/\D/g, '');
  input.value = val ? parseInt(val).toLocaleString() : '';
}

// Confirm delete
function confirmDelete(msg) {
  return confirm(msg || 'Are you sure you want to delete this?');
}

// Image lazy loading
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        observer.unobserve(img);
      }
    });
  });
  document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
}
