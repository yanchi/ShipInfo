<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

final class ContactController extends AbstractController
{
    #[Route('/contact', name: 'app_contact')]
    public function index(): Response
    {
        // お問い合わせデータ
        $contactData = [
            'email' => 'info@ferry-info.com',
            'phone' => '123-456-7890',
            'address' => '123 フェリーサービス通り, 那覇市, 日本',
        ];

        return $this->render('contact/index.html.twig', [
            'contact_data' => $contactData,
        ]);
    }
}
