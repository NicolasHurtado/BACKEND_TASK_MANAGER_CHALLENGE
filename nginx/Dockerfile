FROM nginx:alpine

# Install OpenSSL for certificate generation
RUN apk add --no-cache openssl

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Generate SSL certificates
RUN openssl genrsa -out /etc/nginx/ssl/key.pem 2048 && \
    openssl req -new -key /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/cert.csr \
    -subj "/C=US/ST=State/L=City/O=TaskManager/CN=localhost" && \
    openssl x509 -req -in /etc/nginx/ssl/cert.csr -signkey /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem -days 365 && \
    rm /etc/nginx/ssl/cert.csr

# Set proper permissions
RUN chmod 600 /etc/nginx/ssl/key.pem && \
    chmod 644 /etc/nginx/ssl/cert.pem

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 