window.addEventListener('DOMContentLoaded',
  () => {
    const params = new URLSearchParams(new URL(window.location).search);
    if (params.has('mobile')) {
      document.selectedStyleSheetSet = 'Mobile';
    }
  });
