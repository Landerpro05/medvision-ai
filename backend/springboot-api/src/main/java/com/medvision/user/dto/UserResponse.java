
package com.medvision.user.dto;

import com.medvision.user.User;

import java.util.UUID;

public record UserResponse(
        UUID id,
        String username,
        String email,
        boolean enabled
) {
    public static UserResponse from(User user) {
        return new UserResponse(
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                user.isEnabled()
        );
    }
}
