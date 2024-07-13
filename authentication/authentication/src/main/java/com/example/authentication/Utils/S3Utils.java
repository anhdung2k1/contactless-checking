package com.example.authentication.Utils;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.example.authentication.builder.Base64DecodedMultipartFile;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URL;
import java.util.Base64;
import java.util.Objects;
import java.util.UUID;

@Transactional(rollbackOn = Exception.class)
@RequiredArgsConstructor
@Service
public class S3Utils {

    @Value("${bucket.name}")
    private String bucketName;

    @Autowired
    private AmazonS3 s3Client;

    public URL getS3URL(String filePath, String fileBase64) throws IOException {
        byte[] fileBytes = Base64.getDecoder().decode(fileBase64.split(",")[1]);
        MultipartFile file = new Base64DecodedMultipartFile(fileBytes);
        File fileObj = convertMultiPartFileToFile(file);
        String fileName = filePath + UUID.randomUUID() + "__" + file.getOriginalFilename() + ".jpg";
        s3Client.putObject(new PutObjectRequest(bucketName, fileName, fileObj));
        return s3Client.getUrl(bucketName, fileName);
    }

    private File convertMultiPartFileToFile(MultipartFile file) throws IOException {
        File convertedFile = new File(Objects.requireNonNull(file.getOriginalFilename()));
        try (FileOutputStream fos = new FileOutputStream(convertedFile)) {
            fos.write(file.getBytes());
        } catch (IOException e) {
            throw new IOException("ERROR converting multipart File to file", e);
        }
        return convertedFile;
    }
}