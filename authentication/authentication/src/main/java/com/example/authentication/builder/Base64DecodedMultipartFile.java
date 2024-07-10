package com.example.authentication.builder;

import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;

public class Base64DecodedMultipartFile implements MultipartFile {
    private final byte[] bytes;
    private final String name;
    private final String originalFileName;
    private final String contentType;

    public Base64DecodedMultipartFile(byte[] bytes) {
        this.bytes = bytes;
        this.name = "file";
        this.originalFileName = "file";
        this.contentType = "application/octet-stream"; // You can specify the content type according to your needs
    }
    @Override
    public String getName() {
        return name;
    }

    @Override
    public String getOriginalFilename() {
        return originalFileName;
    }

    @Override
    public String getContentType() {
        return contentType;
    }

    @Override
    public boolean isEmpty() {
        return bytes == null || bytes.length == 0;
    }

    @Override
    public long getSize() {
        return bytes.length;
    }

    @Override
    public byte[] getBytes() throws IOException {
        return bytes;
    }

    @Override
    public InputStream getInputStream() throws IOException {
        return new ByteArrayInputStream(bytes);
    }

    @Override
    public void transferTo(java.io.File dest) throws IOException, IllegalStateException {
        // Not implemented
    }
}