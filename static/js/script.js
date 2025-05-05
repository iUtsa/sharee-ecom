/**
 * Sharee - Online Saree Shop
 * Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initFlashMessages();
    initProductQuantity();
    initProductTabs();
    initProductGallery();
    initReviewForm();
    initAjaxCart();
  });
  
  /**
   * Flash Messages
   * Handle closing of flash messages
   */
  function initFlashMessages() {
    const closeButtons = document.querySelectorAll('.alert .close-btn');
    
    closeButtons.forEach(button => {
      button.addEventListener('click', function() {
        const alert = this.closest('.alert');
        alert.style.opacity = '0';
        setTimeout(() => {
          alert.style.display = 'none';
        }, 300);
      });
    });
    
    // Auto-hide messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
      setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => {
          alert.style.display = 'none';
        }, 300);
      }, 5000);
    });
  }
  
  /**
   * Product Quantity
   * Handle quantity increment/decrement on product pages
   */
  function initProductQuantity() {
    const minusButtons = document.querySelectorAll('.minus-btn');
    const plusButtons = document.querySelectorAll('.plus-btn');
    
    minusButtons.forEach(button => {
      button.addEventListener('click', function() {
        const input = this.parentNode.querySelector('.qty-input');
        let value = parseInt(input.value);
        if (value > 1) {
          input.value = value - 1;
        }
      });
    });
    
    plusButtons.forEach(button => {
      button.addEventListener('click', function() {
        const input = this.parentNode.querySelector('.qty-input');
        let value = parseInt(input.value);
        if (value < 10) {
          input.value = value + 1;
        }
      });
    });
  }
  
  /**
   * Product Tabs
   * Handle tab switching on product detail page
   */
  function initProductTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    if (tabButtons.length) {
      tabButtons.forEach(button => {
        button.addEventListener('click', function() {
          // Remove active class from all buttons
          tabButtons.forEach(btn => btn.classList.remove('active'));
          
          // Add active class to clicked button
          this.classList.add('active');
          
          // Hide all tab panes
          const tabPanes = document.querySelectorAll('.tab-pane');
          tabPanes.forEach(pane => pane.classList.remove('active'));
          
          // Show the corresponding tab pane
          const tabId = this.getAttribute('data-tab');
          document.getElementById(tabId).classList.add('active');
        });
      });
    }
  }
  
  /**
   * Product Gallery
   * Handle thumbnail switching and zoom effect
   */
  function initProductGallery() {
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('main-product-image');
    
    if (thumbnails.length && mainImage) {
      thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
          // Remove active class from all thumbnails
          thumbnails.forEach(thumb => thumb.classList.remove('active'));
          
          // Add active class to clicked thumbnail
          this.classList.add('active');
          
          // Update main image src
          const imgSrc = this.getAttribute('data-src');
          mainImage.src = imgSrc;
        });
      });
      
      // Simple zoom effect
      const zoomGallery = document.querySelector('.zoom-gallery');
      if (zoomGallery) {
        zoomGallery.addEventListener('mousemove', function(e) {
          const { left, top, width, height } = this.getBoundingClientRect();
          const x = (e.clientX - left) / width * 100;
          const y = (e.clientY - top) / height * 100;
          
          mainImage.style.transformOrigin = `${x}% ${y}%`;
        });
        
        zoomGallery.addEventListener('mouseenter', function() {
          mainImage.style.transform = 'scale(1.5)';
        });
        
        zoomGallery.addEventListener('mouseleave', function() {
          mainImage.style.transform = 'scale(1)';
        });
      }
    }
  }
  
  /**
   * Review Form
   * Handle star rating selection
   */
  function initReviewForm() {
    const ratingStars = document.querySelectorAll('.rating-selector i');
    
    if (ratingStars.length) {
      ratingStars.forEach(star => {
        star.addEventListener('click', function() {
          const rating = parseInt(this.getAttribute('data-rating'));
          
          // Update visual stars
          ratingStars.forEach((s, index) => {
            if (index < rating) {
              s.className = 'fas fa-star';
            } else {
              s.className = 'far fa-star';
            }
          });
          
          // Set hidden input value
          const ratingInput = document.createElement('input');
          ratingInput.type = 'hidden';
          ratingInput.name = 'rating';
          ratingInput.value = rating;
          
          // Remove any existing rating input
          const existingInput = document.querySelector('input[name="rating"]');
          if (existingInput) {
            existingInput.remove();
          }
          
          // Add the new rating input
          document.querySelector('.review-form').appendChild(ratingInput);
        });
        
        star.addEventListener('mouseover', function() {
          const rating = parseInt(this.getAttribute('data-rating'));
          
          // Update visual stars on hover
          ratingStars.forEach((s, index) => {
            if (index < rating) {
              s.className = 'fas fa-star';
            } else {
              s.className = 'far fa-star';
            }
          });
        });
        
        // Reset to selected rating on mouseout
        document.querySelector('.rating-selector').addEventListener('mouseout', function() {
          const selectedRating = document.querySelector('input[name="rating"]');
          const rating = selectedRating ? parseInt(selectedRating.value) : 0;
          
          ratingStars.forEach((s, index) => {
            if (index < rating) {
              s.className = 'fas fa-star';
            } else {
              s.className = 'far fa-star';
            }
          });
        });
      });
    }
  }
  
  /**
   * Ajax Cart
   * Handle adding to cart without page refresh
   */
  function initAjaxCart() {
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    
    addToCartForms.forEach(form => {
      form.addEventListener('submit', function(e) {
        // Only use AJAX if browser supports it
        if (window.XMLHttpRequest) {
          e.preventDefault();
          
          const formData = new FormData(this);
          const xhr = new XMLHttpRequest();
          
          xhr.open('POST', this.action, true);
          xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
          
          xhr.onload = function() {
            if (xhr.status === 200) {
              try {
                const response = JSON.parse(xhr.responseText);
                
                if (response.status === 'success') {
                  // Update cart count
                  const cartCountElements = document.querySelectorAll('.cart-count');
                  cartCountElements.forEach(element => {
                    element.textContent = response.cart_count;
                    
                    // Animate the cart icon
                    element.closest('.cart-icon').classList.add('cart-updated');
                    setTimeout(() => {
                      element.closest('.cart-icon').classList.remove('cart-updated');
                    }, 1000);
                  });
                  
                  // Show success message
                  showNotification('Product added to cart successfully!', 'success');
                }
              } catch (error) {
                console.error('Error parsing JSON response:', error);
              }
            }
          };
          
          xhr.onerror = function() {
            console.error('Request failed');
            // If AJAX fails, submit the form normally
            form.submit();
          };
          
          xhr.send(formData);
        }
      });
    });
  }
  
  /**
   * Show notification
   * Display a temporary notification message
   */
  function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i class="notification-icon fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
      </div>
      <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Style the notification
    Object.assign(notification.style, {
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      backgroundColor: type === 'success' ? '#4caf50' : '#2196f3',
      color: 'white',
      padding: '12px 20px',
      borderRadius: '4px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      zIndex: '9999',
      opacity: '0',
      transform: 'translateY(20px)',
      transition: 'all 0.3s ease'
    });
    
    // Style the close button
    const closeBtn = notification.querySelector('.notification-close');
    Object.assign(closeBtn.style, {
      background: 'none',
      border: 'none',
      color: 'white',
      cursor: 'pointer',
      marginLeft: '10px'
    });
    
    // Add event listener to close button
    closeBtn.addEventListener('click', function() {
      hideNotification(notification);
    });
    
    // Show the notification with animation
    setTimeout(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      hideNotification(notification);
    }, 3000);
  }
  
  /**
   * Hide notification
   * Remove notification with animation
   */
  function hideNotification(notification) {
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }